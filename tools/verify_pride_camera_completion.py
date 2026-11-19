"""Verify an input-only Pride completion with MD camera and supported mixtures.

The recording is a local ignored artifact. No practice menu, invulnerability,
state loading, actor edits or world-position overrides are used by this tool.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes
from pride_start_route import prepare


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tape',type=Path,default=ROOT/'build/pride-camera-completion/normal320.polled.tape')
    parser.add_argument('--frames',type=int,default=5819)
    args=parser.parse_args()
    assert args.tape.is_file(),'Provide the local normal-controller route with --tape; recordings are not committed'
    out=ROOT/'build/pride-camera-completion-verified';out.mkdir(parents=True,exist_ok=True)
    report_path=out/'report.json'
    if report_path.exists():
        previous=report_path.read_bytes()
        (out/'previous-report.json').write_bytes(previous)
        history=out/'report-history';history.mkdir(exist_ok=True)
        (history/(hashlib.sha256(previous).hexdigest()+'.json')).write_bytes(previous)
    report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    native='schema = 1\ngame = snes\ndisplay.viewport = md\ngameplay.camera = md\n'
    gameplay=native+'gameplay.levels.pride_lands.pickups = md\ngameplay.levels.pride_lands.leaves = md\ngameplay.levels.pride_lands.contacts = md\ngameplay.simba.roar = md\n'
    gameplay+='gameplay.levels.pride_lands.start = md\n'
    adapted=prepare(args.tape,out/'md-start.polled.tape')
    all_sources=(ROOT/'profiles/pride-lands.ini').read_text()+'\ngameplay.camera = md\ngameplay.levels.pride_lands.leaves = md\ngameplay.levels.pride_lands.contacts = md\ngameplay.simba.roar = md\naudio.effects.world.leaves = md\naudio.effects.simba.roll = md\naudio.effects.world.hyena_pant = md\naudio.effects.world.hyena_jump = md\n'
    results={}
    for scenario,choices in [('camera',native),('gameplay',gameplay),('all',all_sources)]:
        tape=args.tape if scenario=='camera' else adapted
        frames=args.frames+(0 if scenario=='camera' else 3)
        profile=out/(scenario+'.ini');profile.write_text(choices)
        modes={}
        for mode in ('aot','lle'):
            folder=out/(scenario+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(folder/'coverage.json')
            host=ROOT/('dist/LionKing.exe' if scenario=='all' else 'engine/build-win/tlk_headless.exe')
            cmd=[str(host),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),
                 '--resource-profile',str(profile),'--frames',str(frames),'--input-polled',str(tape)]
            if scenario=='all':
                cmd+=['--config',str(config),'--no-pace','--no-audio','--no-record','--dump-window',str(folder/'window.png'),
                      '--dump-scene',str(folder/'scene.json'),'--wav',str(folder/'start.wav'),'--wav-seconds','1']
                # Keep the audio consumer running throughout the route even
                # after the bounded file fills. Otherwise queued, unrendered
                # effects can saturate the MD command queue before the battle.
                env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')
                if (ROOT/'game-data/scenes-v1.cache').exists():cmd+=['--asset-cache',str(ROOT/'game-data/scenes-v1.cache')]
                env['TLK_AUDIO_EVENTS']=str(folder/'events.csv')
                env['TLK_MD_SOUND_COMMANDS']=str(folder/'driver.csv')
            else:cmd+=['--ram-log',str(folder/'game.ram')]
            if mode=='lle':cmd.append('--lle')
            log=folder/'game.log'
            with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=240)
            assert 'Saved resource profile loaded' in log.read_text(errors='replace'),'Source profile rejected'
            value=hashes(log);assert len(value)==2
            if scenario=='all':
                scene=json.loads((folder/'scene.json').read_text());level=scene['level']
                coverage=json.loads((folder/'coverage.json').read_text())
                assert not coverage['missing_poses'] and not coverage['missing_npc_poses'],('Unmapped art on normal MD-camera route',coverage)
                commands=list(csv.DictReader((folder/'driver.csv').open()))
                tracks={int(r['value']) for r in commands if r['selector']=='1'}
                assert {137,134}<=tracks,'Original level and battle tracks were not both reached'
                assert any(r['selector']=='2' and r['value']=='94' for r in commands),'Parent leaf rustle not reached'
                assert any(r['selector']=='2' and r['value']=='165' for r in commands),'Lizard defeat cue not reached'
                stems=list(csv.DictReader((folder/'stems.csv').open()))
                assert len(stems)>1000 and max(int(r['md_peak']) for r in stems)>500,'MD mixture was not rendered'
            else:
                rows=[r.split() for r in (folder/'game.ram').read_text().splitlines()];level=int(rows[-1][6],16)
                assert any(int(r[6],16)==0 and int(r[5],16)<200 for r in rows),'Upper Pride route was not traversed'
            assert level==1,(scenario,mode,'Normal route did not reach next main level',level)
            modes[mode]=value
            print(scenario,mode,'normal power-on first-level completion PASS',flush=True)
        assert modes['aot']==modes['lle'],scenario+' final AOT/LLE hashes differ'
        if scenario!='all':assert (out/(scenario+'-aot/game.ram')).read_bytes()==(out/(scenario+'-lle/game.ram')).read_bytes(),scenario+' tracked gameplay differs'
        results[scenario]=modes
    # Capture the actual mixed Pride encounter, before the level transition.
    folder=out/'all-boss';folder.mkdir(exist_ok=True)
    cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),
         '--resource-profile',str(out/'all.ini'),'--config',str(config),'--frames','4903','--input-polled',str(adapted),
         '--no-pace','--no-audio','--no-record','--dump-window',str(folder/'window.png'),'--dump-scene',str(folder/'scene.json')]
    with (folder/'game.log').open('wb') as stream:subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
    scene=json.loads((folder/'scene.json').read_text());assert scene['level']==0 and scene['stage_detected'],'Mixed encounter window was not Pride'
    report={'result':'PASS','scope':__doc__,'tape':str(args.tape),'tape_sha256':hashlib.sha256(args.tape.read_bytes()).hexdigest(),
            'frames':args.frames,'runs':results,'actual_mixed_pride_window':str(folder/'window.png')}
    report['md_start_controller_route']={'path':str(adapted),'sha256':hashlib.sha256(adapted.read_bytes()).hexdigest(),'extra_polls':3,'frames':args.frames+3}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MD camera, all six gameplay choices and supported full mixture complete Pride Lands PASS',flush=True)


if __name__=='__main__':
    try:main()
    except Exception as error:
        out=ROOT/'build/pride-camera-completion-verified';out.mkdir(parents=True,exist_ok=True)
        (out/'report.json').write_text(json.dumps({'result':'FAIL','scope':__doc__,'error':str(error),
            'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'headless_sha256':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest()},indent=2)+'\n')
        raise
