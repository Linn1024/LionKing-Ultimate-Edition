"""Build maintained menu source selection/native owner, retaining322/324 inputs."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-menu226-integrated';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
patches=ROOT/'engine/cmake/game-patches'
with (out/'game-patch.log').open('wb') as f:
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),
        '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
for label,src in [('host',ROOT/'engine/runner/pride/final/pride_final_host.c'),('resources',out/'game/tlk_resources.c')]:
    cmd=b['compiles'][label].copy();old=(cwd/Path(cmd[cmd.index('-o')+1])).resolve();obj=out/(label+'.obj')
    for flag,value in [('-c',src),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
    if label=='resources':cmd.append('-DTLK_FINAL_MENU_ART_AVAILABLE=1')
    with (out/(label+'-compile.log')).open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==322
paths=[Path(__file__),bp,rsp,out/'game/tlk_resources.c',ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_final_menu_policy.h',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
    *sorted((ROOT/'engine/runner/pride/final').glob('*.inc')),ROOT/'engine/runner/pride/final/pride_final_host.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,compiles=compiles,
    inputs_retained=322,scope='Maintained menu resource leaf/native owner with selected-viewport centre fix and restart reset. Native menu episode saves explicitly unavailable; ordinary gameplay saves retained. Staged, not published; needs current runtime/UI/regression gates.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
