"""Rebuild only menu help text, retaining323/324 staged226 link inputs."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-menu226-integrated';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-menu260-help';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
old='native menu artwork and later title-screen delay remain; independent of nonfinal revival and audio'
new='menu artwork, nonfinal revival and audio are selected independently; later title-screen delay remains native'
maintained=ROOT/'engine/runner/tlk_resources.c';archived=ROOT/'build/pride-menu259-baseline/engine/runner/tlk_resources.c'
assert archived.read_text().count(old)==1
assert maintained.read_text()==archived.read_text().replace(old,new)
with (out/'game-patch.log').open('wb') as log:
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert (out/'game/tlk_resources.c').read_text()==(base/'game/tlk_resources.c').read_text().replace(old,new)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);cmd=compiles['resources'].copy()
previous=(cwd/Path(cmd[cmd.index('-o')+1])).resolve();obj=out/'resources.obj'
for flag,value in (('-c',out/'game/tlk_resources.c'),('-o',obj),('-MT',obj),('-MF',out/'resources.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'resources-compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous];assert len(indices)==1
inputs[indices[0]]=obj.as_posix();compiles['resources']=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert len(linked)==324 and retained==323
paths=[Path(__file__),bp,rsp,maintained,archived,out/'game/tlk_resources.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,compiles=compiles,inputs_retained=retained,
    changes_only_help_string=True,scope='Staged226 with one inaccurate resource scope description corrected. Exact source comparison proves no other maintained/generated resource-source differences;323/324 linked objects retained including host. Not published or fully release-qualified.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),'retained',retained,flush=True)
