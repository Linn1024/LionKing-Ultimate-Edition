"""Verify the native death scene controller against original MD field captures.

This builds the standalone controller/unit target. The player is deliberately
not linked to it until renderer/loader/audio ownership is integrated.
"""
import csv
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-death-controller';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    identity={str(p):digest(ROOT/p) for p in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    timeline_path=ROOT/'build/pride-death-timeline/report.json';timeline=json.loads(timeline_path.read_text())
    assert timeline['result']=='STREAMS_EQUAL_STAGING_DIFFERENT_ADAPTER_OPEN'
    assert timeline['headless_sha256']==identity['engine/build-win/tlk_headless.exe']
    samples_path=ROOT/'build/pride-death-timeline/md/samples.json'
    source_hashes={k.replace('\\','/'):v for k,v in timeline['source_sha256'].items()}
    assert source_hashes[samples_path.relative_to(ROOT).as_posix()]==digest(samples_path)
    rows={r['frame']:r for r in json.loads(samples_path.read_text())}
    counterparts={int(r['md_pose'],16):int(r['native_pose'],16) for r in timeline['pose_art']}
    revival_path=ROOT/'build/pride-revival-reference/report.json';revival=json.loads(revival_path.read_text())
    default_path=ROOT/'build/pride-default-death-reference/report.json';default=json.loads(default_path.read_text())
    for reference,script in ((revival,'pride_revival_reference.py'),(default,'pride_default_death_reference.py')):
        assert reference['result']=='PASS'
        assert reference['source_sha256']['script']==digest(ROOT/'tools'/script)
        assert reference['source_sha256']['trace_source']==digest(ROOT/'tools/md_revival_trace.c')
        assert reference['source_sha256']['trace_dll']==digest(ROOT/'build/md_revival_trace.dll')
        assert reference['source_sha256']['core']==digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll')
    revival_palette_path=ROOT/'build/pride-revival-reference/palettes.json'
    assert revival['source_sha256']['palettes']==digest(revival_palette_path)
    revival_palettes={r['frame']:r['cram'] for r in json.loads(revival_palette_path.read_text())}
    prefix=default['selected_prefix_fields'];default_fields_path=ROOT/f'build/pride-default-death-reference/{prefix}/fields.json'
    assert default['source_sha256']['fields']==digest(default_fields_path)
    default_rows={r['frame']:r for r in json.loads(default_fields_path.read_text())}
    cases=[]
    for number,case in enumerate(timeline['md_deaths']):
        reference=revival['cases'][number];assert reference['death']==case['death']
        final=case['display_skipped']
        cases.append({'death':case['death'],'checkpoint':True,'final':final,'rows':rows,
                      'palettes':revival_palettes,'loop_start':None if final else reference['main_loop_start'],
                      'loop_end':None if final else reference['main_loop_end'],
                      'black':None if final else reference['complete_fade_end'],
                      'owner':None if final else reference['new_actor_owner'],
                      'health':None if final else reference['health_restore_write'],
                      'fade_return':None if final else reference['fade_in_return'],
                      'ready':case['death'] if final else reference['normal_play_jump']})
    dc=default['case'];one=lambda key:dc[key][0] if len(dc[key])==1 else None
    cases.append({'death':dc['death'],'checkpoint':False,'final':False,'rows':default_rows,
                  'palettes':{f:r['cram'] for f,r in default_rows.items()},'loop_start':one('main_loop_start'),
                  'loop_end':one('main_loop_end'),'black':one('complete_fade_end'),'owner':one('new_actor_owner'),
                  'health':dc['health_restored'],'fade_return':one('fade_in_return'),'ready':one('normal_play_jump')})
    assert all(c['ready']-c['death']==(0 if c['final'] else 345 if c['checkpoint'] else 300) for c in cases)
    poses=out/'original-fields.csv'
    with poses.open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(('case','age','field','origin_x','origin_y','camera_x','camera_y',
                                               'final','checkpoint','md_pose','timer','token','x','y','snes_pose','phase'))
        for number,case in enumerate(cases):
            first=case['rows'][case['death']];final=case['final']
            for age in range(1 if final else 249):
                frame=case['death']+age;row=case['rows'][frame]
                if final:pose=timer=token=native=0;phase=8
                else:
                    assert row['camera']==first['camera']
                    pose=row['pose'];timer=row['words'][13]>>8;native=counterparts[pose]
                    cursor=(row['words'][9]<<16)|row['words'][10]
                    token=(cursor-0x7e5b2)//4-1
                    assert cursor==0x7e5b2+(token+1)*4 and 0<=token<33
                    phase=1 if frame<case['loop_start'] else 2 if frame<case['loop_end'] else 3
                writer.writerow((number,age,frame,*first['xy'],*first['camera'],int(final),int(case['checkpoint']),pose,timer,token,*row['xy'],native,phase))
    palettes=out/'original-palettes.csv'
    palette_checks=0
    with palettes.open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(('case','age','checkpoint','index','death_color','next_color','actual'))
        for number,case in enumerate(cases):
            if case['final']:continue
            initial=struct.unpack('<64H',bytes.fromhex(case['palettes'][case['death']]))
            target=struct.unpack('<64H',bytes.fromhex(case['palettes'][case['ready']]))
            assert initial==target
            for age in range(case['ready']-case['death']+1):
                actual=struct.unpack('<64H',bytes.fromhex(case['palettes'][case['death']+age]))
                for i,color in enumerate(actual):
                    writer.writerow((number,age,int(case['checkpoint']),i,initial[i],target[i],color));palette_checks+=1
    phases=out/'original-phases.csv';phase_checks=0
    with phases.open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(('case','age','field','checkpoint','final','phase','events'))
        for number,case in enumerate(cases):
            for frame in range(case['death'],case['ready']+1):
                if case['final']:phase,event=8,16
                else:
                    phase=1 if frame<case['loop_start'] else 2 if frame<case['loop_end'] else 3 if frame<case['black'] else 4 if frame<case['health'] else 5 if frame<case['fade_return'] else 6 if frame<case['ready'] else 7
                    event=1 if frame==case['loop_end'] else 2 if frame==case['black'] else 32 if frame==case['owner'] else 4 if frame==case['health'] else 8 if frame==case['ready'] else 64 if case['checkpoint'] and frame==case['fade_return'] else 0
                writer.writerow((number,frame-case['death'],frame,int(case['checkpoint']),int(case['final']),phase,event));phase_checks+=1
    assert palette_checks==196416 and phase_checks==3070
    states=out/'states';states.mkdir(exist_ok=True)
    commands=[['cmake','--build','engine/build-win','--target','tlk_death_scene_test','-j','4']]
    base=[ROOT/'engine/build-win/tlk_death_scene_test.exe',ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',poses,palettes,phases]
    commands.extend([list(map(str,[*base,mode,states])) for mode in ('--write','--read')])
    for i,command in enumerate(commands):
        with (out/f'run-{i}.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    assert all(digest(ROOT/p)==sha for p,sha in identity.items()),'Standalone target changed a production binary'
    result={'result':'PASS','scope':__doc__,'player_sha256':identity['dist/LionKing.exe'],
            'headless_sha256':identity['engine/build-win/tlk_headless.exe'],
            'controller_test_sha256':digest(ROOT/'engine/build-win/tlk_death_scene_test.exe'),
            'original_pose_motion_fields':2242,'original_palette_word_checks':palette_checks,'original_phase_field_checks':phase_checks,
            'original_nonfinal_deaths':9,'original_final_life_skip':True,'scene_record_bytes':128,
            'checkpoint_ready_age':345,'default_ready_age':300,'checkpoint_health_age':270,'default_health_age':274,
            'checkpoint_respawn_hold_fields':49,'palette_settled_does_not_end_scene':True,
            'cross_process_saved_phases':45,'scene_record_atomic_rejection':True,
            'video_field_pause_duplicate_and_monotonic_guards':True,
            'production_controller_enabled':False,'production_binaries_unchanged':True,
            'source_sha256':{'script':digest(Path(__file__)),'timeline':digest(timeline_path),'revival_reference':digest(revival_path),
                             'default_reference':digest(default_path),'poses':digest(poses),'palettes':digest(palettes),'phases':digest(phases),
                             'controller':digest(ROOT/'engine/runner/tlk_death_scene.c'),
                             'header':digest(ROOT/'engine/runner/tlk_death_scene.h'),
                             'unit':digest(ROOT/'engine/tests/death_scene_test.c')},
            'logs_sha256':{f'run-{i}.log':digest(out/f'run-{i}.log') for i in range(3)},
            'full_first_level_fidelity_complete':False}
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    print('Native death controller:2242 original pose/motion fields,196416 palette words,3070 phase fields and45 cross-process phases PASS',flush=True)


if __name__=='__main__':main()
