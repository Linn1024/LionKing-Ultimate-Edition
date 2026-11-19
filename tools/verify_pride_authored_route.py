"""Verify an authored Pride route from power-on, without planning state loads.

Use local credited controller inputs. Completion of a supported mixture is
bounded evidence and does not prove every first-level resource/state difference.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import wave
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tape',type=Path,required=True)
    parser.add_argument('--frames',type=int,required=True)
    parser.add_argument('--media',action='store_true')
    parser.add_argument('--width',type=int,choices=(256,320),default=320)
    parser.add_argument('--output-root',type=Path,default=ROOT/'build/pride-authored-completion')
    parser.add_argument('--player',type=Path,default=ROOT/'dist/LionKing.exe')
    parser.add_argument('--checkpoint',action='store_true',help='Exercise independent checkpoint MD artwork/palette')
    args=parser.parse_args();assert args.tape.is_file()
    scenario=('media' if args.media else 'gameplay')+('256' if args.width==256 else '')
    out=ROOT/args.output_root/scenario
    out.mkdir(parents=True,exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    choices={}
    for path in ([ROOT/'profiles/pride-lands.ini'] if args.media else [])+[ROOT/'build/pride-route-candidate/resources.ini']:
        for line in path.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith(';'):
                key,value=line.split('=',1);choices[key.strip()]=value.strip()
    if args.media:
        for key in ('audio.effects.world.leaves','audio.effects.simba.roll','audio.effects.world.hyena_pant','audio.effects.world.hyena_jump',
                    'audio.music.pride_health_death','audio.music.pride_game_over'):
            choices[key]='md'
    choices['display.viewport']='md' if args.width==320 else 'snes'
    if args.checkpoint:
        choices['graphics.sprites.checkpoints']='md'
    profile=out/'resources.ini';profile.write_text('\n'.join(key+' = '+value for key,value in choices.items())+'\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    host=(ROOT/args.player) if args.media else ROOT/'engine/build-win/tlk_headless.exe';runs={};coverage={}
    host_identity=digest(host);script_identity=digest(Path(__file__))
    try:
        for mode in ('aot','lle'):
            folder=out/mode;folder.mkdir(exist_ok=True)
            env=os.environ.copy();env.update(TLK_FRAME_LOG=str(folder/'frame-fnv.log'),
                TLK_SPRITE_REPORT=str(folder/'coverage.json'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--frames',args.frames,'--input-polled',args.tape]
            if args.media:
                env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')
                cmd+=['--config',config,'--no-pace','--no-audio','--no-record',
                      '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json',
                      '--wav',folder/'route.wav','--wav-seconds','100','--asset-cache',ROOT/'game-data/scenes-v1.cache']
            else:cmd+=['--ram-log',folder/'game.ram']
            if args.checkpoint and not args.media:cmd+=['--wide',args.width]
            if mode=='lle':cmd+=['--lle']
            with (folder/'game.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            runs[mode]=hashes(folder/'game.log');assert len(runs[mode])==2
            if args.media:
                scene=json.loads((folder/'scene.json').read_text());assert scene['level']==1,('media did not finish Pride',mode,scene['level'])
                coverage[mode]=json.loads((folder/'coverage.json').read_text())
                assert not coverage[mode]['missing_poses'] and not coverage[mode]['missing_npc_poses'],coverage[mode]
                commands=list(csv.DictReader((folder/'driver.csv').open()))
                tracks={int(row['value']) for row in commands if row['selector']=='1'}
                assert {137,134}<=tracks,'Both level and hyena music were not observed'
                stems=list(csv.DictReader((folder/'stems.csv').open()))
                assert len(stems)>1000 and max(int(row['md_peak']) for row in stems)>500
            else:
                rows=[r.split() for r in (folder/'game.ram').read_text().splitlines()]
                assert int(rows[-1][6],16)==1,('Gameplay did not finish Pride',mode)
                assert any(int(r[0])>1000 and int(r[6],16)==0 and int(r[4],16)>500 and int(r[5],16)<200
                           for r in rows),'Upper Pride route was not observed outside the bonus/player origin'
            print('Ordinary power-on Pride completion',mode,'PASS',flush=True)
        assert runs['aot']==runs['lle'],'Final guest hashes differ'
        if not args.media:
            for name in ('game.ram','frame-fnv.log'):
                assert (out/'aot'/name).read_bytes()==(out/'lle'/name).read_bytes(),name
        else:
            for mode in ('aot','lle'):
                with wave.open(str(out/mode/'route.wav'),'rb') as audio:
                    assert audio.getframerate()==48000 and audio.getnchannels()==2 and audio.getsampwidth()==2
                    assert audio.getnframes()>30*48000
            assert (out/'aot/route.wav').read_bytes()==(out/'lle/route.wav').read_bytes(),'Mixed route audio differs'
        report={'result':'PASS','scope':__doc__,'media':args.media,'width':args.width,'frames':args.frames,
                'player_sha256':digest(ROOT/args.player),'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
                'executed_host_sha256':host_identity,'verifier_sha256':script_identity,'checkpoint_sources':args.checkpoint,
                'tape':str(args.tape),'tape_sha256':digest(args.tape),'profile_sha256':digest(profile),
                'normal_first_level_completion_verified':True,'loaded_states':False,'actor_or_world_edits':False,
                'execution_modes':runs,'sprite_coverage':coverage,'full_first_level_fidelity_complete':False}
        if args.media:report['exact_mixed_wav_sha256']=digest(out/'aot/route.wav')
        assert digest(host)==host_identity and digest(Path(__file__))==script_identity
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    except Exception as error:
        report_path.write_text(json.dumps({'result':'FAIL','scope':__doc__,'error':str(error),
            'tape_sha256':digest(args.tape),'frames':args.frames,'media':args.media,'width':args.width,
            'player_sha256':digest(ROOT/'dist/LionKing.exe'),'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe')},indent=2)+'\n')
        raise


if __name__=='__main__':main()
