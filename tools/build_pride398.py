"""Build the Available MD preset and its two existing resource editors."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride390';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride398';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
for layer,source,target in (('game-patches',ROOT/'engine',out/'game'),('frontend-patches',ROOT/'engine',out/'shared')):
    with (out/(layer+'.log')).open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake'/layer),'--snesrecomp',str(source),'--out',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
(out/'frontend').mkdir(exist_ok=True)
shutil.copy2(ROOT/'build/pride382/frontend/sdl_main.c',out/'frontend/sdl_main.c')
shutil.copy2(out/'shared/tlk_resource_editor_sdl.h',out/'frontend/tlk_resource_editor_sdl.h')
shutil.copy2(ROOT/'build/pride382/frontend/tlk_resource_editor_selftest.h',out/'frontend/tlk_resource_editor_selftest.h')
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
matches=[r for r in rows if r.get('output','').replace('\\','/').endswith('/runner/tlk_menu_imgui.cpp.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(matches)==1
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('host',b['compiles']['host'],None),('menu',argv(matches[0]['command']),ROOT/'engine/runner/tlk_menu_imgui.cpp')]
for label,template,src in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    if src:cmd[cmd.index('-c')+1]=str(src)
    if label=='host':
        i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-len(tasks)
paths=[Path(__file__),bp,rsp,*[ROOT/name for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_resources.h','engine/runner/tlk_resource_editor_sdl.h','engine/runner/tlk_menu_imgui.cpp','engine/cmake/frontend-patches/zzz-resource-help.hunks')],out/'game/tlk_resources.c',out/'frontend/sdl_main.c',out/'frontend/tlk_resource_editor_sdl.h']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
