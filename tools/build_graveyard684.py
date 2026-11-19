"""Build MD socket images/colors and installed terrain-tag hyena decisions."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
bp=ROOT/'build/graveyard659/build-report.json';b=bound(bp);base=bp.parent
out=ROOT/'build/graveyard684';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c',False),('wide',b['compiles']['wide'],None,False),('sprites',b['compiles']['sprites'],out/'game/tlk_md_sprites.c',False),('pride_data',b['compiles']['pride_data'],ROOT/'engine/runner/tlk_pride_data.c',False),('graveyard_gameplay',b['compiles']['graveyard_gameplay'],ROOT/'engine/runner/tlk_graveyard_gameplay.c',False),('graveyard_data',b['compiles']['graveyard_gameplay'],ROOT/'engine/runner/tlk_graveyard_data.c',True)]
db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
rows=[r for r in db if r.get('output','').replace('\\','/').endswith('/bankc1_part17_v2.c.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(rows)==1
cmd=argv(rows[0]['command']);tasks.append(('hyena_unit',cmd,(cwd/cmd[cmd.index('-c')+1]).resolve(),False))
for label,template,src,added in tasks:
 cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
 for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
 if src:cmd[cmd.index('-c')+1]=str(src)
 with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
 if added:inputs.append(obj.as_posix())
 else:
  indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old);inputs[indices[0]]=obj.as_posix()
 compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
paths=[Path(__file__),bp,rsp,*[ROOT/'engine/runner'/p for p in ('tlk_resources.c','tlk_wide.c','tlk_md_sprites.c','tlk_pride_data.c','tlk_graveyard_gameplay.c','tlk_graveyard_data.c','tlk_graveyard_data.h','aot_pace.h')],ROOT/'engine/generated/resources/pride_sprite_map.h',ROOT/'tools/graveyard_sprite_catalog.py',out/'game/tlk_resources.c',out/'game/tlk_md_sprites.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'),flush=True)
