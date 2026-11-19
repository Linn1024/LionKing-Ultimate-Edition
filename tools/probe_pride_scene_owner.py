"""Verify native preparation/return scheduling against the owned MD scene clock.

This isolates CPU readiness. Backend health, rendering and audio ownership must
still be integrated; it is not a selectable or complete death-behavior adapter.
"""
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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',nargs='+',choices=('native','both'),default=['native','both'])
    parser.add_argument('--modes',nargs='+',choices=('control','scheduled'),default=['control','scheduled'])
    parser.add_argument('--sdl',action='store_true')
    parser.add_argument('--reuse',action='store_true',help='Reanalyse unchanged-executable captures without replay')
    args=parser.parse_args();host='sdl' if args.sdl else 'headless'
    out=ROOT/('build/pride-scene-owner-'+host);out.mkdir(exist_ok=True)
    report=out/'report.json';prior=json.loads(report.read_text()) if args.reuse else None
    if prior:
        assert prior['result']=='CPU_PREPARATION_TIMING_VERIFIED_RENDER_AUDIO_HEALTH_OPEN'
        assert prior['sources']==args.sources and prior['modes']==args.modes and prior['host']==host
        for name,sha in prior['source_sha256'].items():
            if name not in ('engine/CMakeLists.txt','tools/probe_pride_scene_owner.py'):assert digest(ROOT/name)==sha,name
    report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/('engine/build-win/tlk_scene_owner_'+('sdl' if args.sdl else 'probe')+'.exe');binary_hash=digest(binary)
    if prior:assert prior['probe_sha256']==binary_hash
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    results={}
    for source in args.sources:
        for mode in args.modes:
            case=source+'-'+mode;folder=out/case;folder.mkdir(exist_ok=True)
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE'):env[key]=str(folder)
            env['TLK_NATIVE_BANK_APPLY']=env['TLK_SCENE_PREPARE_APPLY']='1'
            env['TLK_SCENE_OWNER_ENABLE']=str(int(mode=='scheduled'))
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
            if args.sdl:
                env['TLK_AUDIO_EVENTS']=str(folder/'audio-events.csv');env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv')
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--lle','--frames','5400',
                '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape']
            if args.sdl:cmd+=['--config',config,'--no-pace','--no-audio','--no-record','--wav',folder/'route.wav',
                '--wav-seconds','100','--dump-window',folder/'window.png','--dump-png',folder/'picture.png']
            else:cmd+=['--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
            if args.reuse:
                for name,sha in prior['runs'][case]['artifacts_sha256'].items():assert digest(folder/name)==sha,(case,name)
            else:
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            events=list(csv.DictReader((folder/'owner-events.csv').open()));fields=list(csv.DictReader((folder/'owner-fields.csv').open()))
            begin=[r for r in events if r['event']=='begin'];assert len(begin)==1
            start=int(begin[0]['field']);points={}
            for r in events:points.setdefault(r['event'],[]).append(r)
            normal=int(points['normal'][0]['field'])-start;actor=int(points['native_actor'][0]['field'])-start
            health_request=int(points['native_health'][0]['field'])-start
            health=min(int(r['field'])-start for r in fields if int(r['native_health']))
            if mode=='control':
                baseline=ROOT/('build/pride-scene-prepare-sdl' if args.sdl else 'build/pride-scene-prepare')/(source+'-combined')
                assert hashes(folder/'run.log')==hashes(baseline/'run.log'),case
                if args.sdl:assert wav_data(folder/'route.wav')==wav_data(baseline/'route.wav'),case
                else:assert digest(folder/'route.ram')==digest(baseline/'route.ram'),case
            else:
                assert actor<=254 and normal==345,(case,actor,normal,health)
                assert len(points['shorten_display'])==len(points['skip_post_health_wait'])==len(points['checkpoint_hold_count'])==1
                assert len(points['hold_call'])==len(points['hold_return']) and len(points['hold_release'])==1
                assert int(points['hold_release'][0]['age'])==296
                transitions={int(r['age']):int(r['events']) for r in fields if int(r['events'])}
                for age,value in ((225,1),(249,2),(254,32),(270,4),(296,64),(345,8)):
                    assert transitions[age]==value,(case,age,transitions)
                with (ROOT/'build/pride-revival-scene/original-revival.csv').open() as oracle:
                    reference={int(r['age']):r for r in csv.DictReader(oracle) if r['case']=='0'}
                selected=[r for r in fields if 270<=int(r['age'])<=344];assert len(selected)==75
                for r in selected:
                    expected=reference[int(r['age'])]
                    assert int(r['draw_pose'],16)==int(expected['snes_pose']) and int(r['raw_timer'])==int(expected['timer']),(case,r,expected)
                baseline=ROOT/('build/pride-scene-prepare-sdl' if args.sdl else 'build/pride-scene-prepare')/(source+'-combined')
                a=(folder/'normal-wram.bin').read_bytes();b=(baseline/'normal-wram.bin').read_bytes()
                for p,n in ((0x10000,16000),(0x18800,0x2780),(0x1ba00,0x1d80),(0x1d780,0x880),(0x1e000,0xf00)):
                    assert a[p:p+n]==b[p:p+n],(case,'Prepared scene region differs',p)
            peak=None
            music_handoff=None;md_programs=[]
            if args.sdl:
                samples=array.array('h');samples.frombytes(wav_data(folder/'route.wav')[-48000*4:]);peak=max(map(abs,samples));assert peak>0
                assert pixels(folder/'window.png')[:2]==(512,448)
                if (folder/'audio-events.csv').exists():
                    for row in csv.DictReader((folder/'audio-events.csv').open()):
                        stack=bytes.fromhex(row['stack']);offset=5 if row['return0']=='2d16' else 6 if row['return0']=='2d4d' else -1
                        if offset<0 or len(stack)<offset+3:continue
                        caller=(stack[offset+2]<<16)|((int.from_bytes(stack[offset:offset+2],'little')+1)&65535)
                        field=int(row['frame'])+1
                        if row['event']=='0000' and caller==0xc329fa and field>=start:music_handoff=field-start
                if (folder/'md-commands.csv').exists():
                    md_programs=[int(r['value']) for r in csv.DictReader((folder/'md-commands.csv').open()) if r['selector']=='1']
                if source=='both':
                    assert music_handoff==normal and md_programs[-2:]==[430,137],(case,music_handoff,md_programs)
            at_normal=next((r for r in fields if int(r['age'])==345),None)
            results[case]={'guest':hashes(folder/'run.log'),'native_health_age':health,'native_actor_age':actor,
                'native_restore_request_age':health_request,
                'normal_age':normal,'balanced_native_wait_calls':len(points.get('hold_call',[])),
                'backend_health_matches_md_clock':health==270,'production_death_behavior_enabled':False,
                'original_md_revival_art_and_timer_fields':75 if mode=='scheduled' else 0,
                'backend_idle_timer_at_model_ready':int(at_normal['raw_timer']) if at_normal else None,
                'original_md_idle_timer_at_ready':5,
                'idle_timer_handoff_verified':mode=='scheduled' and at_normal is not None and int(at_normal['raw_timer'])==5,
                'last_second_peak':peak,
                'level_music_handoff_age':music_handoff,'md_music_program_sequence':md_programs,
                'artifacts_sha256':{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}}
            print(host,case,'backend health/actor/normal ages',health,actor,normal,'native wait calls',len(points.get('hold_call',[])),'CPU ownership PASS',flush=True)
    assert digest(binary)==binary_hash
    report.write_text(json.dumps({'result':'CPU_PREPARATION_TIMING_VERIFIED_RENDER_AUDIO_HEALTH_OPEN','scope':__doc__,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'host':host,'sources':args.sources,'modes':args.modes,'probe_sha256':binary_hash,'runs':results,
        'production_death_behavior_enabled':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),
            ROOT/'tools/pride_scene_owner_probe.c',ROOT/'tools/pride_scene_prepare_probe.c',ROOT/'tools/pride_scene_template.h',
            ROOT/'tools/pride_native_bank_probe.c',ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/CMakeLists.txt',
            ROOT/'build/pride-revival-scene/original-revival.csv')}},indent=2)+'\n')


if __name__=='__main__':main()
