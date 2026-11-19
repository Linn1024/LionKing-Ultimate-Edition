"""Rebuild only independent porcupine voice timing and its frontend registration."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-battle319';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-porcupine327';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
original=cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
for patches,src,target in (('game-patches',ROOT/'engine',out/'game'),('final-frontend-patches',original,out/'frontend')):
    with (out/(patches+'.log')).open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake'/patches),'--snesrecomp',str(src),'--out',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(original/name,out/'frontend'/name)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
for label,src in (('audio',out/'game/tlk_audio.c'),('resources',out/'game/tlk_resources.c'),('host',ROOT/'engine/runner/pride/final/pride_final_host.c')):
    cmd=b['compiles'][label].copy();old=Path(cmd[cmd.index('-o')+1]);obj=out/(label+'.obj')
    for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    if label in ('audio','resources'):cmd+=['-DTLK_PORCUPINE_VOICE_TIMING_AVAILABLE=1']
    if label=='host':
        i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==321 and len(linked)==324
paths=[Path(__file__),bp,rsp,out/'game/tlk_audio.c',out/'game/tlk_resources.c',out/'frontend/sdl_main.c',*[ROOT/name for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_resources.c','engine/runner/tlk_porcupine_voice_policy.h','engine/cmake/final-frontend-patches/porcupine-attack.hunks','engine/cmake/TlkPrideFinalPlayer.cmake')]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Selected MD porcupine FM105 at original counter28 seam under either gameplay source; native sound queue retained. No guest writes/new save state or asset changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
