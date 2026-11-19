"""Build Stampede/Exile presentation and verified shared sound extensions."""
import json,subprocess,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest,argv
from pride_arena_history import bound
bp=ROOT/'build/graveyard720/build-report.json';b=bound(bp);base=bp.parent;out=ROOT/'build/next743';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);tasks=[]
for label in ('resources','audio','wide','sprites','assets','pride_data','roar','lizard'):
 src=out/'game'/('tlk_md_sprites.c' if label=='sprites' else 'tlk_'+label+'.c') if label in ('resources','audio','sprites') else None
 tasks.append((label,b['compiles'][label],src,False))
db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd));row=next(r for r in db if r.get('output','').replace('\\','/').endswith('/tlk_leaves.c.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256'])
tasks.append(('leaves',argv(row['command']),ROOT/'engine/runner/tlk_leaves.c',False));tasks.append(('next_scene_data',b['compiles']['graveyard_data'],ROOT/'engine/runner/tlk_next_scene_data.c',True))
for label,template,src,added in tasks:
 cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
 for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
 if src:cmd[cmd.index('-c')+1]=str(src)
 with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
 if added:inputs.append(obj.as_posix())
 else:
  ix=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(ix)==1,(label,old);inputs[ix[0]]=obj.as_posix()
 compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
paths=[Path(__file__),bp,rsp,*[ROOT/'engine/runner'/p for p in ('tlk_resources.c','tlk_wide.c','tlk_md_sprites.c','tlk_audio.c','tlk_md_assets.c','tlk_pride_data.c','tlk_next_scene_data.c','tlk_next_scene_data.h','tlk_md_sprites.h','tlk_md_sprite_format.inc','tlk_lizard_audio.c','tlk_leaves.c','tlk_roar.c')],ROOT/'engine/generated/resources/pride_sprite_map.h',ROOT/'engine/generated/resources/next_scene_metadata.h',ROOT/'tools/next_scene_pairs.json']
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'))
