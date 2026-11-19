"""Build the viewport-centred caption renderer; retain unrelated player objects."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-menu260-help';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-caption268';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'patch.log').open('wb') as log:
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
wide=bound(ROOT/'build/pride-continue-token46/build-report.json')
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
for label,source,original in (('wide',ROOT/'engine/runner/pride/final/pride_final_wide.c',wide['compiles']['wide']),('resources',out/'game/tlk_resources.c',b['compiles']['resources'])):
    cmd=original.copy();previous=(cwd/Path(cmd[cmd.index('-o')+1])).resolve();obj=out/(label+'.obj')
    for flag,value in (('-c',source),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous];assert len(indices)==1,(label,indices)
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert len(linked)==324 and retained==322
paths=[Path(__file__),bp,rsp,ROOT/'engine/runner/tlk_wide.c',ROOT/'engine/runner/tlk_resources.c',out/'game/tlk_resources.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,
    scope='Pride opening caption screen-centred for native falling letters and MD picture, independent of source and camera clamp. Retains vertical animation/baseline, guest state and all unrelated objects. Presentation change; focused caption verification only.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
