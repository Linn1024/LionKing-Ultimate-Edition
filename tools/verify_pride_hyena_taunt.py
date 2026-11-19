"""Verify MD hyena taunt sound and all eight artwork poses on ordinary inputs."""
import csv
import json
import os
import re
import subprocess
import wave
from audit_scenes import ROOT
from verify_windows import hashes,pixels
from pride_hyena_taunt_art import PAIRS


def main():
    out=ROOT/'build/pride-hyena-taunt';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    native=out/'native.ini';native.write_text('schema = 1\ngame = snes\n')
    base=['--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md')]
    head=str(ROOT/'engine/build-win/tlk_headless.exe');sdl=str(ROOT/'dist/LionKing.exe')
    def run(log,cmd,env=None):
        with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
    prefix_log=out/'prefix.log'
    run(prefix_log,[head,*base,'--resource-profile',str(native),'--frames','3850','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape')])
    used=int(re.search(r'tape_words_used=(\d+)',prefix_log.read_text()).group(1))
    tape=out/'stop.polled.tape';tape.write_bytes((ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[:used*2]+bytes(5000))
    ready=out/'ready.state';prep=out/'prepare.log'
    run(prep,[head,*base,'--resource-profile',str(native),'--frames','3980','--input-polled',str(tape),'--save-at','3980',str(ready)])
    consumed=int(re.search(r'tape_words_used=(\d+)',prep.read_text()).group(1))
    suffix=out/'after.polled.tape';suffix.write_bytes(tape.read_bytes()[consumed*2:])
    results={};audio={};early_windows={}
    for mode in ('native','md-aot','md-lle','sibling'):
        stem=out/mode;profile=stem.with_suffix('.ini')
        choices='schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.simba.hurt = md\n'
        if mode.startswith('md-'):choices+='audio.effects.world.hyena_taunt = md\n'
        if mode=='sibling':choices+='audio.effects.world.hyena_jump = md\n'
        profile.write_text(choices)
        env=os.environ.copy()
        for key,extension in [('TLK_AUDIO_EVENTS','-events.csv'),('TLK_AUDIO_STEMS','-stems.csv'),('TLK_MD_SOUND_COMMANDS','-commands.csv'),('TLK_HYENA_TAUNT_TRACE','-entries.csv')]:env[key]=str(stem)+extension
        run(stem.with_suffix('.log'),[sdl,*base,'--config',str(config),'--resource-profile',str(profile),'--load',str(ready),
            '--input-polled',str(suffix),'--frames','4350','--no-pace','--no-audio','--no-record','--wav',str(stem)+'.wav','--wav-seconds','10',
            *(['--lle'] if mode=='md-lle' else [])],env)
        entries=list(csv.DictReader(open(str(stem)+'-entries.csv')))
        assert len(entries)==2 and {row['actor'] for row in entries}=={'ba13'},(mode,entries)
        assert sum(int(row['emitted']) for row in entries)==(2 if mode.startswith('md-') else 0)
        commands=list(csv.DictReader(open(str(stem)+'-commands.csv')))
        cue=[row for row in commands if row['selector']=='19' and row['value']=='3']
        assert len(cue)==(2 if mode.startswith('md-') else 0),(mode,cue)
        events=list(csv.DictReader(open(str(stem)+'-events.csv')))
        callbacks=[row for row in events if row['event']=='001e' and
                   ((int.from_bytes(bytes.fromhex(row['stack'])[5:8],'little')+1)&0xffffff)==0xc14262]
        assert len(callbacks)==2,(mode,'Native delayed callback count',callbacks)
        stems=list(csv.DictReader(open(str(stem)+'-stems.csv')))
        peaks=[]
        for event in callbacks:
            start=int(event['frame']);end=min([int(row['frame']) for row in events if int(row['frame'])>start]+[4350])
            window=[int(row['native_peak']) for row in stems if start+8<=int(row['frame'])<end]
            assert window,(mode,'No isolated native voice window',start,end)
            peaks.append(max(window))
        if mode.startswith('md-'):assert max(peaks)==0,(mode,'Native taunt cue leaked',peaks)
        else:assert min(peaks)>1000,(mode,'Native delayed cue inaudible',peaks)
        results[mode]={'hashes':hashes(stem.with_suffix('.log')),'entry_frames':[int(row['frame']) for row in entries],
                       'pcm3_calls':len(cue),'native_delayed_peaks':peaks}
        with wave.open(str(stem.with_suffix('.wav')),'rb') as stream:
            assert stream.getnchannels()==2 and stream.getsampwidth()==2 and stream.getframerate()==48000
            audio[mode]=stream.readframes(stream.getnframes())
        first_entry=int(entries[0]['frame']);first_native=int(callbacks[0]['frame'])
        begin=sum(int(row['samples']) for row in stems if int(row['frame'])<=first_entry)*4
        end=sum(int(row['samples']) for row in stems if int(row['frame'])<=first_native)*4
        early_windows[mode]=(begin,end)
        print(mode,'two ordinary-entry taunts, independent cue and native suppression PASS',flush=True)
    assert results['md-aot']==results['md-lle'] and audio['md-aot']==audio['md-lle']
    assert results['native']==results['sibling'] and audio['native']==audio['sibling']
    assert audio['native']!=audio['md-aot']
    # Before the delayed native cue, the only changed sound is the added MD
    # entry voice. This proves audible contribution, not just later muting.
    assert early_windows['native']==early_windows['md-aot']
    begin,end=early_windows['native'];assert end>begin
    assert audio['native'][:begin]==audio['md-aot'][:begin]
    assert audio['native'][begin:end]!=audio['md-aot'][begin:end], 'MD entry voice did not contribute before native cue'
    art={};seen=set()
    for source,choices in [('snes',''),('frames','graphics.sprites.enemies.hyenas.frames = md\n'),
                           ('palette','graphics.sprites.enemies.hyenas.palette = md\n'),('both','graphics.sprites.enemies.hyenas = md\n')]:
        stem=out/('art-'+source);profile=stem.with_suffix('.ini');profile.write_text('schema = 1\ngame = snes\n'+choices)
        env=os.environ.copy();env['TLK_SPRITE_OBJECTS']=str(stem)+'.csv';env['TLK_SPRITE_REPORT']=str(stem)+'-coverage.json'
        run(stem.with_suffix('.log'),[sdl,*base,'--config',str(config),'--resource-profile',str(profile),'--frames','4060',
            '--input-polled',str(tape),'--no-pace','--no-audio','--no-record','--dump-window',str(stem)+'.png'],env)
        objects=list(csv.DictReader(open(str(stem)+'.csv')))
        observed={int(row['pose'],16) for row in objects if row['position']=='ba1b' and row['palette']=='6'}
        assert {p for p,_ in PAIRS}<=observed,(source,'Unobserved taunt art',observed)
        coverage=json.loads(open(str(stem)+'-coverage.json').read())
        assert not coverage['missing_npc_poses'],coverage
        art[source]=hashes(stem.with_suffix('.log'));seen|=observed
    assert len({tuple(sorted(value.items())) for value in art.values()})==1,'Art source changed guest state'
    assert all(pixels(out/'art-snes.png')!=pixels(out/('art-'+name+'.png')) for name in ('frames','palette','both'))
    report={'result':'PASS','scope':__doc__,'ordinary_input_prefix_polls':used,'actor':'ba13','audio':results,
            'art_hashes':art,'all_eight_taunt_poses_observed':True,'native_palette':6,'original_md_palette':3,
            'audible_md_entry_before_native_cue':True,
            'common_audio_choices':['MD level/battle music','MD cub hurt to isolate overlapping voice tails']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
