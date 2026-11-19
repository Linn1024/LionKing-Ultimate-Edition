"""Audit prepared-renderer new-process resume with real controller state.

Whole-trace, glyph and window verification are separate from endpoint parity.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes
from verify_windows import pixels


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def frame_records(path,width):
    if not path.exists():return {}
    result={};size=56+width*224*12
    with path.open('rb') as f:
        assert f.read(16)==b'PRDRGB01'+struct.pack('<II',width,224)
        while raw:=f.read(size):
            assert len(raw)==size;age=struct.unpack_from('<I',raw)[0]
            if age in result:assert result[age]==raw
            result[age]=raw
    return result


def glyph_records(folder):
    events=folder/'prepared-objects.csv'
    if not events.exists():return []
    events=rows(events);raw=(folder/'prepared-fonts.bin').read_bytes()
    assert raw[:8]==b'PRDHUD01' and len(raw)==8+2104*len(events)
    return [(int(e['field']),raw[8+n*2104:8+(n+1)*2104]) for n,e in enumerate(events)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save-at',type=int,default=4703)
    parser.add_argument('--width',type=int,choices=(256,320),default=256)
    parser.add_argument('--graphics',choices=('native','all'),default='native')
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-prepared-state/pilot'))
    parser.add_argument('--save-mode',choices=('aot','lle'),default='aot')
    parser.add_argument('--load-mode',choices=('aot','lle'),default='aot')
    args=parser.parse_args();out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'build/pride-prepared-state';binary=base/'prepared-state-probe.exe';build_path=base/'build-report.json'
    build=json.loads(build_path.read_text());assert digest(binary)==build['runs']['probe']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    identities={str(build_path.relative_to(ROOT)).replace('\\','/'):digest(build_path),
                str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))}
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('md' if args.width==320 else 'snes')+'\n'+('graphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\ngraphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n' if args.graphics=='all' else '')+'graphics.sprites.checkpoints.frames = md\ngraphics.sprites.checkpoints.palette = md\n')
    neutral=base/'neutral.polled.tape';neutral.write_bytes(bytes(4096))
    state=out/'checkpoint.private-state';results={}
    for name,load in (('baseline',False),('resumed',True)):
        folder=out/name;folder.mkdir(exist_ok=True);env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames','5400','--input-polled',neutral if load else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
             '--ram-log',folder/'route.ram','--wide',args.width,'--wide-png',folder/'picture.png']
        if load:cmd+=['--load',state]
        else:cmd+=['--save-at',args.save_at,state]
        if (args.load_mode if load else args.save_mode)=='lle':cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        results[name]=dict(exit_code=result.returncode,guest=hashes(folder/'run.log'),
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        print(name,'exit',result.returncode,flush=True)
    exact=results['baseline']['exit_code']==results['resumed']['exit_code']==0 and results['baseline']['guest']==results['resumed']['guest']
    tracked=False;events=False;rendered=False;glyphs=False;image=False
    if exact:
        a=(out/'baseline/route.ram').read_bytes().splitlines(keepends=True)
        b=(out/'resumed/route.ram').read_bytes().splitlines(keepends=True)
        tracked=b==a[-len(b):] and len(b)==5400-args.save_at
        expected=[r for r in rows(out/'baseline/owner-events.csv') if int(r['field'])>args.save_at]
        events=rows(out/'resumed/owner-events.csv')==expected
        start=[int(r['field']) for r in rows(out/'baseline/owner-events.csv') if r['event']=='begin']
        assert len(start)==1
        before=frame_records(out/'baseline/render-owned.rgb',args.width)
        after=frame_records(out/'resumed/render-owned.rgb',args.width)
        rendered=after=={age:value for age,value in before.items() if start[0]+age>args.save_at}
        for filename in ('render-fields.csv','prepared-objects.csv','restore-fields.csv','restore-events.csv'):
            source=out/'baseline'/filename;target=out/'resumed'/filename
            expected=[r for r in rows(source) if int(r['field'])>args.save_at] if source.exists() else []
            actual=rows(target) if target.exists() else []
            rendered=rendered and actual==expected
        glyphs=glyph_records(out/'resumed')==[(f,r) for f,r in glyph_records(out/'baseline') if f>args.save_at]
        image=pixels(out/'baseline/picture.png')==pixels(out/'resumed/picture.png')
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    report=dict(result='AUDITED',scope=__doc__,runs=results,save_at=args.save_at,save_mode=args.save_mode,load_mode=args.load_mode,
        endpoint_guest_exact=exact,remaining_tracked_ram_exact=tracked,remaining_owner_events_exact=events,
        remaining_composition_and_scene_trace_exact=rendered,remaining_installed_glyphs_exact=glyphs,final_composed_image_exact=image,
        state_sha256=digest(state) if state.exists() else None,binary_sha256=digest(binary),source_sha256=identities,
        width=args.width,graphics=args.graphics,prepared_graphics_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('New-process endpoint exact='+str(exact)+'; tracked RAM='+str(tracked)+'; owner events='+str(events),flush=True)


if __name__=='__main__':main()
