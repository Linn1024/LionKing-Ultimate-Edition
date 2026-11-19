"""Check independent actor sounds through original input routes and a pant fixture.

The pant fixture selects the original hyena handler/animation event in a saved
actor record. It verifies the callback and sound isolation, not completion.
"""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import struct
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-actor-audio';out.mkdir(parents=True,exist_ok=True)
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    cases=[('bounce','audio.effects.simba.bounce',1370,1450,0x11,0xc36686,2,123),
           ('porcupine','audio.effects.world.porcupine',1460,1530,0x15,0xc15cb0,2,105),
           ('hyena','audio.effects.world.hyena_hurt',3910,4010,0x20,0xc1458d,19,4),
           ('roll-right','audio.effects.simba.roll',2190,2260,0x0a,0xc355c2,0,0),
           ('roll-left','audio.effects.simba.roll',2470,2540,0x0a,0xc35769,0,0),
           ('hyena-jump','audio.effects.world.hyena_jump',3860,3910,0x1e,0xc1496e,0,0),
           ('hyena-pant','audio.effects.world.hyena_pant',3850,3890,0x1f,0xc146cc,19,7)]
    report={'scope':__doc__,'controlled_callback_fixtures':['hyena-pant'],'cases':{}}
    for name,leaf,start,end,event,caller,selector,value in cases:
        extra=''
        case_tape=tape
        prepare_profile=out/(name+'-prepare.ini');prepare_profile.write_text('schema = 1\ngame = snes\n'+extra)
        original=out/(name+'.state')
        command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(prepare_profile),
                 '--frames',str(start),'--input-polled',str(case_tape),'--save-at',str(start),str(original)]
        with (out/(name+'-prepare.log')).open('wb') as stream:
            prepare_env=os.environ.copy()
            if name=='hyena-pant':prepare_env.update(TLK_WRAM_DUMP=str(start),TLK_WRAM_DIR=str(out))
            subprocess.run(command,cwd=ROOT,env=prepare_env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        if name=='hyena-pant':
            ram=(out/f'hl_wram_{start}.bin').read_bytes();snapshot=bytearray(original.read_bytes());offset=snapshot.find(ram)
            assert offset>=0 and snapshot.find(ram,offset+1)==-1,'Fixture WRAM is not unique'
            actors=[a for a in range(0xb213,0xc213,0x80) if 0xc13c83<=int.from_bytes(ram[a+0x30:a+0x33],'little')<0xc14b00]
            assert len(actors)==1,'Expected one existing Pride hyena'
            actor=actors[0]
            struct.pack_into('<I',snapshot,offset+actor+0x30,0xc145d3)
            struct.pack_into('<H',snapshot,offset+actor+0x2e,2)
            original.write_bytes(snapshot)
        used=int(re.search(r'tape_words_used=(\d+)',(out/(name+'-prepare.log')).read_text()).group(1))
        after=out/(name+'.polled.tape');after.write_bytes(case_tape.read_bytes()[used*2:])
        results={};peaks={}
        for mode in ('native','md-aot','md-lle','other-choice'):
            stem=out/(name+'-'+mode)
            choices=extra+'audio.music.pride_lands = md\n'
            if mode.startswith('md-'):choices+=leaf+' = md\n'
            elif mode=='other-choice':
                other='audio.effects.world.health_bug'
                choices+=other+' = md\n'
            profile=stem.with_suffix('.ini');profile.write_text('schema = 1\ngame = snes\n'+choices)
            env=os.environ.copy()
            for variable,suffix in [('TLK_AUDIO_EVENTS','-events.csv'),('TLK_AUDIO_STEMS','-stems.csv'),
                                    ('TLK_MD_SOUND_COMMANDS','-driver.csv')]:env[variable]=str(stem)+suffix
            command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                     '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                     '--config',str(ROOT/'build/windows-smoke/host.ini'),'--load',str(original),
                     '--input-polled',str(after),'--frames',str(end),'--no-pace','--no-audio','--no-record',
                     '--wav',str(stem)+'.wav','--wav-seconds','3']
            if mode=='md-lle':command.append('--lle')
            with stem.with_suffix('.log').open('wb') as stream:
                subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
            assert 'Saved resource profile loaded' in stem.with_suffix('.log').read_text(),(name,mode,'Source profile was rejected')
            events=list(csv.DictReader(Path(str(stem)+'-events.csv').open()))
            selected=[r for r in events if int(r['event'],16)==event and
                      ((int.from_bytes(bytes.fromhex(r['stack'])[5:8],'little')+1)&0xffffff)==caller]
            assert selected,(name,mode,'Original callback was not reached')
            commands=list(csv.DictReader(Path(str(stem)+'-driver.csv').open()))
            mapped=[r for r in commands if int(r['selector'])==selector and int(r['value'])==value]
            assert len(mapped)==(len(selected) if selector and mode.startswith('md-') else 0),(name,mode,mapped,selected)
            if not selector:
                assert all(int(r['selector'])==1 for r in commands),(name,'MD rolling must not invent a replacement cue',commands)
            # Last hyena recoil excludes the earlier cub-hurt cry; other cases
            # have an isolated first event after the music-stop packet drained.
            cue=int(selected[-1 if name in ('hyena','hyena-pant') else 0]['frame'])
            following=min([int(r['frame']) for r in events if int(r['frame'])>cue]+[end])
            assert following>cue+8,(name,mode,'No isolated audio window')
            stems=list(csv.DictReader(Path(str(stem)+'-stems.csv').open()))
            peak=max(int(r['native_peak']) for r in stems if cue+8<=int(r['frame'])<following)
            peaks[mode]=peak
            results[mode]={'hashes':hashes(stem.with_suffix('.log')),'cue_count':len(mapped),'native_peak':peak}
        assert results['md-aot']==results['md-lle'],name+' execution modes differ'
        if name=='hyena-pant':
            # This controlled native callback has a silent tail after Music
            # Off; its MD addition is proved by the original command and WAV,
            # rather than claiming independently audible native suppression.
            assert peaks['native']==peaks['other-choice'],(name,peaks)
        else:assert peaks['native']>1000 and peaks['other-choice']>1000,(name,peaks)
        assert peaks['md-aot']==0,(name,'Native actor cue leaked',peaks)
        assert (out/(name+'-native.wav')).read_bytes()!=(out/(name+'-md-aot.wav')).read_bytes()
        report['cases'][name]=results
        print(name,'controlled original callback' if name=='hyena-pant' else 'original route','independent source and AOT/LLE PASS',flush=True)
    report['result']='PASS';(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
