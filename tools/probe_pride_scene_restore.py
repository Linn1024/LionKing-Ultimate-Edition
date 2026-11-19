"""Verify deferred health/roar publication and canonical neutral-idle handoff."""
import argparse
import array
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):return list(csv.DictReader(path.open()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',nargs='+',choices=('native','both'),default=['native','both'])
    parser.add_argument('--modes',nargs='+',choices=('control','deferred','canonical'),default=['control','canonical'])
    parser.add_argument('--sdl',action='store_true');parser.add_argument('--reuse',action='store_true')
    args=parser.parse_args();host='sdl' if args.sdl else 'headless'
    out=ROOT/('build/pride-scene-restore-'+host);out.mkdir(exist_ok=True)
    report=out/'report.json';prior=json.loads(report.read_text()) if args.reuse else None
    binary=ROOT/f'engine/build-win/tlk_scene_restore_{"sdl" if args.sdl else "probe"}.exe';exe=digest(binary)
    if prior:
        assert prior['result']=='RESTORE_AND_HANDOFF_VERIFIED_RENDER_PLAYER_OPEN' and prior['probe_sha256']==exe
        assert prior['sources']==args.sources and prior['modes']==args.modes
        for name,sha in prior['source_sha256'].items():
            if name not in ('engine/CMakeLists.txt','tools/probe_pride_scene_restore.py'):assert digest(ROOT/name)==sha,name
    report.write_text('{"result":"RUNNING"}\n');results={}
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    oracle=ROOT/'build/pride-revival-scene/original-revival.csv'
    expected={int(r['age']):r for r in rows(oracle) if r['case']=='0'}
    for source in args.sources:
        for mode in args.modes:
            case=source+'-'+mode;folder=out/case;folder.mkdir(exist_ok=True)
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
            env['TLK_NATIVE_BANK_APPLY']=env['TLK_SCENE_PREPARE_APPLY']=env['TLK_SCENE_OWNER_ENABLE']='1'
            env['TLK_SCENE_RESTORE_ENABLE']=str(int(mode!='control'));env['TLK_SCENE_RESTORE_CANONICAL']=str(int(mode=='canonical'))
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
            env.pop('TLK_NATIVE_BANK_RECORD',None);env.pop('TLK_WATCH',None)
            env['TLK_AUDIO_EVENTS']=str(folder/'audio-events.csv');env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv')
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--lle','--frames','5400',
                '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape','--dump-png',folder/'picture.png']
            if args.sdl:cmd+=['--config',config,'--no-pace','--no-audio','--no-record','--wav',folder/'route.wav',
                '--wav-seconds','100','--dump-window',folder/'window.png']
            else:cmd+=['--ram-log',folder/'route.ram']
            if args.reuse:
                for name,sha in prior['runs'][case]['artifacts_sha256'].items():assert digest(folder/name)==sha,(case,name)
            else:
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            events=rows(folder/'owner-events.csv');fields=rows(folder/'owner-fields.csv');restore=rows(folder/'restore-events.csv')
            start=int(next(r['field'] for r in events if r['event']=='begin'))
            health=min(int(r['field'])-start for r in fields if int(r['native_health']))
            normal=int(next(r['field'] for r in events if r['event']=='normal'))-start
            actor=int(next(r['field'] for r in events if r['event']=='native_actor'))-start
            assert actor<=254 and normal==345 and health==(225 if mode=='control' else 270),(case,health,actor,normal)
            baseline=ROOT/f'build/pride-scene-owner-{host}/{source}-scheduled'
            if mode=='control':
                assert hashes(folder/'run.log')==hashes(baseline/'run.log'),case
                if args.sdl:assert wav_data(folder/'route.wav')==wav_data(baseline/'route.wav'),case
                else:assert digest(folder/'route.ram')==digest(baseline/'route.ram'),case
                assert not restore
            else:
                by={}
                for r in restore:by.setdefault(r['event'],[]).append(r)
                assert len(by['request_health'])==len(by['request_roar'])==len(by['publish'])==1
                assert int(by['request_health'][0]['age'])==int(by['request_roar'][0]['age'])==225
                publish=by['publish'][0];assert int(publish['age'])==270
                assert publish['health']==by['request_health'][0]['value'] and publish['roar']==by['request_roar'][0]['value']
                assert by['hold_health_widget'] and all(225<=int(r['age'])<270 for r in by['hold_health_widget'])
                assert all(int(r['native_health'])==0 for r in fields if int(r['field'])-start<270)
                state=rows(folder/'restore-fields.csv')
                assert all(int(r['roar'])==0 for r in state if 225<=int(r['age'])<270)
                assert all(r['roar']==publish['roar'] for r in state if 270<=int(r['age'])<=345)
                if mode=='canonical':assert by['retain_ready_idle'] and all(int(r['age'])==345 for r in by['retain_ready_idle'])
            end=345 if mode=='canonical' else 344
            selected=[r for r in fields if 270<=int(r['field'])-start<=end];assert len(selected)==end-269
            for r in selected:
                ref=expected[int(r['field'])-start]
                assert int(r['draw_pose'],16)==int(ref['snes_pose']) and int(r['raw_timer'])==int(ref['timer']),(case,r,ref)
            a=(folder/'normal-wram.bin').read_bytes();b=(baseline/'normal-wram.bin').read_bytes()
            for p,n in ((0x10000,16000),(0x18800,0x2780),(0x1ba00,0x1d80),(0x1d780,0x880),(0x1e000,0xf00)):assert a[p:p+n]==b[p:p+n],(case,p)
            peak=None;exact_audio=None;audio_difference=None
            if args.sdl:
                pcm=wav_data(folder/'route.wav');tail=array.array('h');tail.frombytes(pcm[-48000*4:]);peak=max(map(abs,tail));assert peak>0
                assert pixels(folder/'window.png')[:2]==(512,448);exact_audio=pcm==wav_data(baseline/'route.wav')
                if not exact_audio:
                    old=wav_data(baseline/'route.wav');per_field=48000*357366/21477272
                    prefix=int((start+225-1)*per_field)*4
                    assert pcm[:prefix]==old[:prefix],(case,'Audio changed before deferred requests')
                    first=next(i for i,(x,y) in enumerate(zip(pcm,old)) if x!=y)
                    reverse=next(i for i,(x,y) in enumerate(zip(reversed(pcm),reversed(old))) if x!=y)
                    audio_difference={'first_stereo_sample':first//4,'last_stereo_sample':(len(pcm)-1-reverse)//4,
                        'first_approx_field':first/4/per_field,'last_approx_field':(len(pcm)-1-reverse)/4/per_field,
                        'last_second_exact':pcm[-192000:]==old[-192000:],'prefix_before_request_exact':True}
            results[case]={'guest':hashes(folder/'run.log'),'health_age':health,'actor_age':actor,'normal_age':normal,
                'revival_art_and_timer_fields':len(selected),'widget_holds':sum(r['event']=='hold_health_widget' for r in restore),
                'idle_timer_at_ready':int(next(r['raw_timer'] for r in fields if int(r['field'])-start==345)),
                'canonical_idle_calls':sum(r['event']=='retain_ready_idle' for r in restore),
                'exact_prior_schedule_audio':exact_audio,'last_second_peak':peak,
                'prior_audio_difference':audio_difference,
                'artifacts_sha256':{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}}
            print(host,case,'health/actor/normal',health,actor,normal,len(selected),'original revival fields PASS',flush=True)
    assert digest(binary)==exe
    report.write_text(json.dumps({'result':'RESTORE_AND_HANDOFF_VERIFIED_RENDER_PLAYER_OPEN','scope':__doc__,
        'host':host,'sources':args.sources,'modes':args.modes,'probe_sha256':exe,'runs':results,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'production_behavior_enabled':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),oracle,
            ROOT/'tools/pride_scene_restore_probe.c',ROOT/'tools/pride_scene_owner_probe.c',ROOT/'tools/pride_scene_prepare_probe.c',
            ROOT/'tools/pride_scene_template.h',ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/CMakeLists.txt')}},indent=2)+'\n')


if __name__=='__main__':main()
