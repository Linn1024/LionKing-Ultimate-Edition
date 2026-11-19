"""Exercise seven original pickup callbacks and independent MD audio choices.

These are controlled fixtures: a captured ground bug receives another original
bug descriptor before contact. They verify sound dispatch and original pickup
effects, not an unmodified gameplay completion route. No ROM is changed.
"""
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-pickup-audio';out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['TLK_WRAM_DUMP']='1030';env['TLK_WRAM_DIR']=str(out)
    original=out/'before-pickup.state'
    command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--frames','1030','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
             '--save-at','1030',str(original)]
    with (out/'prepare.log').open('wb') as stream:
        subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
    ram=(out/'hl_wram_1030.bin').read_bytes();snapshot=original.read_bytes()
    offset=snapshot.find(ram)
    assert offset>=0 and snapshot.find(ram,offset+1)==-1,'WRAM is not uniquely identifiable in this build'
    assert struct.unpack_from('<I',ram,0xb697)[0]==0xc58939,'Fixture actor changed'
    used=int(re.search(r'tape_words_used=(\d+)',(out/'prepare.log').read_text()).group(1))
    tape=out/'after.polled.tape'
    tape.write_bytes((ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[used*2:(used+100)*2])
    snes=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    cases=[('health_bug',0x11,97),('full_health_bug',0x12,98),('life_bug',0x10,112),
           ('life_bug_alt',0x31,112),('roar_bug',0x20,116),
           ('harmful_bug',0x21,117),('harmful_bug_alt',0x23,117)]
    report={'scope':__doc__,'cases':{}}
    for name,marker,effect in cases:
        leaf=name.removesuffix('_alt')
        descriptor=int.from_bytes(snes[0xbe14+marker*6:0xbe17+marker*6],'little')
        state=bytearray(snapshot)
        struct.pack_into('<I',state,offset+0xb697,descriptor)
        struct.pack_into('<H',state,offset+0x2004,4)
        fixture=out/(name+'.state');fixture.write_bytes(state)
        results={}
        for mode in ('native','md-aot','md-lle','other-choice'):
            stem=out/(name+'-'+mode)
            choices='audio.music.pride_lands = md\n'
            if mode.startswith('md-'):choices+='audio.effects.world.'+leaf+' = md\n'
            elif mode=='other-choice':
                other='health_bug' if leaf!='health_bug' else 'full_health_bug'
                choices+='audio.effects.world.'+other+' = md\n'
            profile=stem.with_suffix('.ini');profile.write_text('schema = 1\ngame = snes\n'+choices)
            env=os.environ.copy()
            for variable,suffix in [('TLK_AUDIO_EVENTS','-events.csv'),('TLK_AUDIO_STEMS','-stems.csv'),
                                    ('TLK_MD_SOUND_COMMANDS','-driver.csv')]:env[variable]=str(stem)+suffix
            command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                     '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                     '--config',str(ROOT/'build/windows-smoke/host.ini'),'--load',str(fixture),
                     '--input-polled',str(tape),'--frames','1100','--no-pace','--no-audio','--no-record',
                     '--wav',str(stem)+'.wav','--wav-seconds','2']
            if mode=='md-lle':command.append('--lle')
            with stem.with_suffix('.log').open('wb') as stream:
                subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
            events=list(csv.DictReader(Path(str(stem)+'-events.csv').open()))
            pickup=[r for r in events if r['actor']=='b693']
            assert len(pickup)==1,(name,mode,pickup)
            start=int(pickup[0]['frame'])
            commands=list(csv.DictReader(Path(str(stem)+'-driver.csv').open()))
            fm=[int(r['value']) for r in commands if r['selector']=='2']
            assert fm==([effect] if mode.startswith('md-') else []),(name,mode,fm)
            stems=list(csv.DictReader(Path(str(stem)+'-stems.csv').open()))
            # Allow the native music-stop packet already queued after loading
            # to drain before inspecting this isolated pickup sound window.
            peak=max(int(r['native_peak']) for r in stems if start+8<=int(r['frame'])<=1100)
            assert (peak==0) if mode.startswith('md-') else (peak>1000),(name,mode,peak)
            results[mode]={'hashes':hashes(stem.with_suffix('.log')),'fm_commands':fm,'native_peak':peak}
        assert results['md-aot']==results['md-lle'],name+' differs between execution modes'
        assert (out/(name+'-native.wav')).read_bytes()!=(out/(name+'-md-aot.wav')).read_bytes(),name+' audio did not change'
        report['cases'][name]={'marker':marker,'descriptor':hex(descriptor),'results':results}
        print(name,'original callback, isolated source and AOT/LLE PASS',flush=True)
    report['result']='PASS'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
