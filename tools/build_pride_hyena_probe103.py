"""Correct real stack range and integrate the source-change restart callback."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

parent=ROOT/'build/pride-hyena-probe97';bp=parent/'build-report.json';prior=bound(bp)
out=ROOT/'build/pride-hyena-probe103';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
frontend=out/'frontend';cmd=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
    '--snesrecomp',str(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'),'--out',str(frontend)]
with (out/'patch.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,frontend/name)
inputs=argv('link '+(parent/'link.rsp').read_text())[1:];compiles=dict(prior['compiles'])
for label,source in [('host',ROOT/'engine/runner/pride/final/pride_final_host.c'),('probe',ROOT/'engine/runner/tlk_hyena_probe.c')]:
    command=prior['compiles'][label].copy();old=Path(command[command.index('-o')+1])
    for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:command[command.index(flag)+1]=str(value)
    if label=='host':
        i=next(i for i,p in enumerate(command) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));command[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(frontend/'sdl_main.c').as_posix()+'"'
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    match=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(match)==1
    inputs[match[0]]=(out/(label+'.obj')).as_posix();compiles[label]=command
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==323 and sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
paths=[Path(__file__),bp,rsp,ROOT/'engine/runner/tlk_hyena_probe.c',ROOT/'engine/runner/tlk_hyena_probe.h',ROOT/'engine/cmake/final-frontend-patches/hyena-walking-probe.hunks',frontend/'sdl_main.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,
    unchanged_candidate97_inputs=321,published=False,fresh_full_graph_claimed=False,original_game_objects_or_assets_modified=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
