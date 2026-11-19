"""Build independently scoped Graveyard effects and three read-only original event seams."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/cant-wait579';bp=base/'build-report.json';b=bound(bp)
hyena=ROOT/'build/pride-hyena-voice72/build-report.json';h=bound(hyena)
out=ROOT/'build/graveyard596';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('audio',b['compiles']['audio'],out/'game/tlk_audio.c'),('hyena_audio',h['compiles']['hyena'],ROOT/'engine/runner/tlk_hyena_audio.c')]
for label,suffix in [('pickup_audio','/runner/tlk_pickup_audio.c.obj'),('ledge_audio','/runner/tlk_ledge_audio.c.obj'),('bone_unit','/bankc1_part03_v2.c.obj'),('sound_unit','/bankc2_part15_v2.c.obj')]:
    rows=[r for r in db if r.get('output','').replace('\\','/').endswith(suffix) and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(rows)==1,(label,len(rows))
    cmd=argv(rows[0]['command']);tasks.append((label,cmd,(cwd/cmd[cmd.index('-c')+1]).resolve()))
for label,template,source in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d')),('-c',source)):cmd[cmd.index(flag)+1]=str(value)
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))};retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-len(tasks)
paths=[Path(__file__),bp,hyena,rsp,*[source for _,_,source in tasks],*[ROOT/name for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_graveyard_audio_metadata.h','engine/runner/aot_pace.h','engine/runner/tlk_resources.c','engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks')]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'),flush=True)
