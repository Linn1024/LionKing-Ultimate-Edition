"""Replace only resources object; bind semantic parents independent of insertions."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

parent=ROOT/'build/pride-hyena-probe103';bp=parent/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-resource-tree118';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
patch=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')]
with (out/'patch.log').open('wb') as f:subprocess.run(patch,stdout=f,stderr=subprocess.STDOUT,check=True)
cmd=b['compiles']['resources'].copy();old=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c',out/'game/tlk_resources.c'),('-o',out/'resources.obj'),('-MT',out/'resources.obj'),('-MF',out/'resources.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
pre=cmd.copy();pre[pre.index('-c')]='-E';pre[pre.index('-o')+1]=str(out/'resources.i');subprocess.run(pre,cwd=cwd,check=True)
inputs=argv('link '+(parent/'link.rsp').read_text())[1:];matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(matches)==1
inputs[matches[0]]=(out/'resources.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==323 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==322
compiles=dict(b['compiles']);compiles['resources']=cmd
paths=[Path(__file__),bp,ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_resource_parent.h',out/'game/tlk_resources.c',out/'resources.i',rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,unchanged_candidate103_inputs=322,
    only_resource_graph_changed=True,published=False,fresh_full_graph_claimed=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
