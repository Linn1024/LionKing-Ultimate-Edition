"""Rebuild only the renderer for per-line native opening-title centring."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-porcupine327';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/level-caption343';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['wide'].copy();old=Path(cmd[cmd.index('-o')+1]);obj=out/'wide.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'wide.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1;inputs[indices[0]]=obj.as_posix()
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==323
compiles=dict(b['compiles']);compiles['wide']=cmd
paths=[Path(__file__),bp,rsp,ROOT/'engine/runner/tlk_wide.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Later main-level falling titles centred per line; native glyph art, palette, animation and guest state retained. Pride independent caption renderer unchanged.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
