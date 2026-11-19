"""Build second-level animation sounds with existing compiled/interpreter parser boundaries."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/cant-wait560';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/cant-wait565';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
rows=[x for x in db if x.get('output','').replace('\\','/').endswith('/runner/tlk_roar.c.obj') and (cwd/x['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(rows)==1
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('audio',b['compiles']['audio'],out/'game/tlk_audio.c'),('roar',argv(rows[0]['command']),ROOT/'engine/runner/tlk_roar.c')]
for label,template,source in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d')),('-c',source)):cmd[cmd.index(flag)+1]=str(value)
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-len(tasks)
paths=[Path(__file__),bp,rsp,*[ROOT/name for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_cw_audio_metadata.h','engine/runner/tlk_roar.c','engine/runner/tlk_resources.c')],out/'game/tlk_audio.c',out/'game/tlk_resources.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'),flush=True)
