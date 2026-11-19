"""Verify original revival pose selection and new-process scene continuation.

Standalone component; the native reload/renderer/audio coordinator is still
required before exposing MD death gameplay in the player.
"""
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import bitmap,snes_frame,md_frame


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-revival-scene';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    identities={p:digest(ROOT/p) for p in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    ref_path=ROOT/'build/pride-revival-art/reference.json';ref=json.loads(ref_path.read_text());assert ref['result']=='PASS'
    assert ref['checkpoint_revivals']==8 and ref['completed_video_fields']==736 and ref['all_revivals_same_art_clock']
    bindings={'script':ROOT/'tools/pride_revival_art_reference.py','core':ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
        'inputs':ROOT/'build/md-next-levels-replay/frames.json','revival_reference':ROOT/'build/pride-revival-reference/report.json',
        'fields':ROOT/'build/pride-revival-art/fields.json','rom':ROOT/'Lion King, The (World).md'}
    for k,p in bindings.items():assert ref['source_sha256'][k]==digest(p),k
    for r in ref['pictures']:assert r['sha256']==digest(ref_path.parent/('age-'+str(r['age'])+'.png'))
    rows=json.loads(bindings['fields'].read_text())
    default_path=ROOT/'build/pride-default-death-reference/report.json';default=json.loads(default_path.read_text());assert default['result']=='PASS'
    default_fields=default_path.parent/str(default['selected_prefix_fields'])/'fields.json'
    assert default['source_sha256']['fields']==digest(default_fields)
    catalog_path=ROOT/'build/pride-sprites/catalog.json';catalog=json.loads(catalog_path.read_text())
    pairs={}
    for r in catalog['exact_matches']:
        for p in r['md']:pairs.setdefault(int(p,16),[]).append(int(r['snes'],16)|0xc00000)
    fixture=out/'original-revival.csv';art=[]
    with fixture.open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(('case','age','checkpoint','md_pose','snes_pose','timer','md_cursor'))
        for r in rows:
            matches=pairs[r['pose']];assert len(matches)==1,(r['pose'],matches)
            assert r['timer_word']&255==0
            writer.writerow((r['case'],r['age'],1,r['pose'],matches[0],r['timer_word']>>8,r['cursor']))
        death=default['case']['death'];default_rows=json.loads(default_fields.read_text())
        selected=[r for r in default_rows if 254<=r['frame']-death<=300];assert len(selected)==47
        for r in selected:
            assert len(pairs[r['pose']])==1 and r['words'][13]&255==0
            writer.writerow((8,r['frame']-death,0,r['pose'],pairs[r['pose']][0],r['words'][13]>>8,
                             (r['words'][9]<<16|r['words'][10])&0xffffff))
    seen=sorted({r['pose'] for r in rows});assert len(seen)==13
    for md_pose in seen:
        native=pairs[md_pose][0]
        a=bitmap(snes,snes_frame(snes,native&0x3fffff),False,with_origin=True)
        b=bitmap(md,md_frame(md,md_pose),True,with_origin=True)
        assert a==b,(hex(native),hex(md_pose),'Anchored indexed artwork differs')
        art.append({'snes':hex(native),'md':hex(md_pose),'origin':a[:2],'size':a[2:4],
                    'indexed_pixels':len(a[4]),'indexed_sha256':hashlib.sha256(a[4]).hexdigest()})
    # A valid inactive record under model2; model3 must reject its identity.
    legacy=bytearray(128);legacy[:8]=b'TLKDSC01';struct.pack_into('<II',legacy,8,1,128)
    identity=bytearray(76);identity[:11]=b'TLKDEATH002'
    identity[12:44]=hashlib.sha256(snes).digest();identity[44:76]=hashlib.sha256(md).digest()
    legacy[16:48]=hashlib.sha256(identity).digest();legacy[96:]=hashlib.sha256(legacy).digest()
    old=out/'model2-record.bin';old.write_bytes(legacy)
    commands=[['cmake','--build','engine/build-win','--target','tlk_revival_scene_test','-j','4']]
    test=ROOT/'engine/build-win/tlk_revival_scene_test.exe'
    for mode in ('--write','--read'):
        commands.append(list(map(str,[test,ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',fixture,
                                      mode,out/'records.bin',old])))
    for i,cmd in enumerate(commands):
        with (out/f'run-{i}.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    assert all(digest(ROOT/p)==sha for p,sha in identities.items())
    result={'result':'PASS','scope':__doc__,'player_sha256':identities['dist/LionKing.exe'],
        'headless_sha256':identities['engine/build-win/tlk_headless.exe'],'test_sha256':digest(test),
        'completed_original_video_fields':783,'checkpoint_fields':736,'default_fields':47,
        'paired_revival_frames':12,'paired_idle_frames':1,'original_art':art,
        'saved_records_sha256':digest(out/'records.bin'),
        'cross_process_saved_fields':783,'continuation_fields_per_record':100,'model2_records_rejected':True,
        'production_binaries_unchanged':True,'production_controller_enabled':False,
        'source_sha256':{'script':digest(Path(__file__)),'reference':digest(ref_path),'catalog':digest(catalog_path),
            'default':digest(default_path),'default_fields':digest(default_fields),'fixture':digest(fixture),
            'controller':digest(ROOT/'engine/runner/tlk_death_scene.c'),'header':digest(ROOT/'engine/runner/tlk_death_scene.h'),
            'unit':digest(ROOT/'engine/tests/revival_scene_test.c'),'legacy':digest(old)},
        'logs_sha256':{f'run-{i}.log':digest(out/f'run-{i}.log') for i in range(3)}}
    report.write_text(json.dumps(result,indent=2)+'\n')
    print('Revival artwork/clock:783 original fields,13 anchored image pairs,783 new-process records x100 fields PASS',flush=True)


if __name__=='__main__':main()
