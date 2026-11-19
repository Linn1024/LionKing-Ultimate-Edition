"""Relink host with the early installed-scene failure check."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride379';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride382';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
original=cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
with (out/'frontend-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),'--snesrecomp',str(original),'--out',str(out/'frontend')],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(original/name,out/'frontend'/name)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);cmd=compiles['host'].copy();old=Path(cmd[cmd.index('-o')+1]);obj=out/'host.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'host.d')):cmd[cmd.index(flag)+1]=str(value)
i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
with (out/'host-compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1;inputs[indices[0]]=obj.as_posix();compiles['host']=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-1
paths=[Path(__file__),bp,rsp,out/'frontend/sdl_main.c',ROOT/'engine/cmake/final-frontend-patches/zz-prepared-scene-startup.hunks']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Retain379 prepared contact/palette implementation; report missing scene data before dependent artwork checks.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
