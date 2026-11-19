"""Rebuild only the final host for the title-menu scene guard; retain installed audio/gameplay/renderers."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/graveyard644';bp=base/'build-report.json';b=bound(bp);out=ROOT/'build/graveyard652';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/'host.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'host.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'host-compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1;inputs[indices[0]]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll');compiles=dict(b['compiles']);compiles['host']=cmd
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))};assert sum(b['link_inputs_sha256'].get(p)==h for p,h in linked.items())==len(linked)-1
paths=[Path(__file__),bp,rsp,ROOT/'engine/runner/pride/final/pride_final_host.c',ROOT/'engine/runner/pride/final/pride_final_title_navigation.inc']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'),flush=True)
