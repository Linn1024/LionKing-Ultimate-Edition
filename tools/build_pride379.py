"""Build player loading prepared contact maps and immutable palette recipes."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/cant-wait372';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride379';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
matches=[r for r in rows if r.get('output','').replace('\\','/').endswith('/runner/tlk_contact_map.c.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(matches)==1
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('assets',b['compiles']['assets'],ROOT/'engine/runner/tlk_md_assets.c'),('host',b['compiles']['host'],None),('contacts',argv(matches[0]['command']),ROOT/'engine/runner/tlk_contact_map.c')]
for label,template,src in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    if src:cmd[cmd.index('-c')+1]=str(src)
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-len(tasks)
paths=[Path(__file__),bp,rsp,*[ROOT/name for name in ('engine/runner/tlk_md_assets.c','engine/runner/tlk_md_assets_cache.inc','engine/runner/tlk_resources.c','engine/runner/tlk_contact_map.c','engine/runner/tlk_contact_map.h','engine/runner/sdl_main.c','engine/runner/headless_main.c')],out/'game/tlk_resources.c']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Scene-v2 packages include prepared Pride contact tables and Cant Wait immutable palette recipes. Installed playback does not decode scenes/contact tables or hydrate palette recipes; missing/outdated supplied data rejects startup.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
