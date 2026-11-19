"""Record all displayed Pride pose/palette pairs, including palette0 effects."""
import csv
import ctypes as C
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-effect-coverage';out.mkdir()
    source=ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json';prior=bound(source)
    reference=source.parent/'full-aot'
    tree=[json.loads(x) for x in (reference/'tree.jsonl').read_text().splitlines()]
    stop=next(r['field'] for r in tree if r['level']==1)-1
    module_path=ROOT/'build/pride-sprite-assets/verification/report.json';module=bound(module_path);assert module['result']=='PASS'
    library=module_path.parent/'prepared.dll';lib=C.CDLL(str(library))
    lib.TlkMdSpriteAssetsReadFile.argtypes=[C.c_char_p]
    assert lib.TlkMdSpriteAssetsReadFile(str(ROOT/'build/pride-sprite-assets/sprites.assets').encode())
    assert lib.TlkMdSpriteAssetsActivate()
    lib.TlkMdSpritesRole.argtypes=[C.c_uint];lib.TlkMdSpritesDrawRole.argtypes=[C.c_uint,C.c_uint]
    lib.TlkMdSpritesBounds.argtypes=[C.c_uint,*([C.POINTER(C.c_int)]*4)]
    commands={};checks={};classifications={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();cmd=prior['commands']['full-aot'].copy()
        for flag,value in [('--frames',stop),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if mode=='lle':cmd.append('--lle')
        commands[mode]=cmd
        env=dict(clean,TLK_SPRITE_OBJECTS=str(folder/'objects.csv'),TLK_SPRITE_REPORT=str(folder/'sprites.json'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[mode+'_exit']=rc==0
        rows=list(csv.DictReader((folder/'objects.csv').open()));classified=[]
        for row in rows:
            pose=int(row['pose'],16);palette=int(row['palette']);args=[C.c_int() for _ in range(4)]
            mapped=bool(lib.TlkMdSpritesBounds(pose,*map(C.byref,args)))
            classified.append(dict(**row,mapped=mapped,role=lib.TlkMdSpritesRole(pose),draw_role=lib.TlkMdSpritesDrawRole(pose,palette)))
        classifications[mode]=classified
        (folder/'classified.json').write_text(json.dumps(classified,indent=2)+'\n')
        print(mode,rc,len(rows),'pairs','unknown',[(r['pose'],r['position'],r['palette']) for r in classified if not r['mapped']],flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:re.findall(pattern,(p/'run.log').read_text())
    expected=[r for r in rows(reference) if int(r[0])<=stop]
    checks['all_pride_guest_fields_neutral']=len(expected)==stop and rows(out/'aot')==rows(out/'lle')==expected
    for name in ('window.png','scene.json','audio.wav','objects.csv','sprites.json','classified.json','tree.jsonl'):
        checks['modes_'+name]=digest(out/'aot'/name)==digest(out/'lle'/name)
    checks['classification_nonempty']=bool(classifications['aot'])
    paths=[Path(__file__),source,module_path,library,ROOT/'build/pride-sprite-assets/sprites.assets',ROOT/'engine/generated/resources/pride_sprite_map.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,last_pride_field=stop,
                every_displayed_pose_palette_pair_logged=True,route_only_not_complete_renderer_claim=True,
                mapped_pairs=sum(r['mapped'] for r in classifications['aot']),total_pairs=len(classifications['aot']),
                unknown_pairs=[r for r in classifications['aot'] if not r['mapped']],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
