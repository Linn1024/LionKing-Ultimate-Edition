"""Build independent vulture health/contact data and level-restart integration."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/graveyard609';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/graveyard621';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
front=Path(next(x for x in b['compiles']['host'] if x.startswith('-DTLK_PRIDE_FRONTEND_SOURCE=')).split('=',1)[1].strip('"')).parent
patches=out/'frontend-patches';patches.mkdir(exist_ok=True);hunk=ROOT/'engine/cmake/final-frontend-patches/zzzz-graveyard-gameplay.hunks';shutil.copy2(hunk,patches/hunk.name)
with (out/'frontend-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),'--snesrecomp',str(front),'--out',str(out/'frontend')],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(front/name,out/'frontend'/name)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c',False),('audio',b['compiles']['audio'],out/'game/tlk_audio.c',False),('sprites',b['compiles']['sprites'],out/'game/tlk_md_sprites.c',False),('hitbox_data',b['compiles']['hitbox_data'],ROOT/'engine/runner/tlk_hitbox_data.c',False),('host',b['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c',False),('graveyard_gameplay',b['compiles']['probe'],ROOT/'engine/runner/tlk_graveyard_gameplay.c',True)]
for label,suffix in [('hitboxes','/runner/tlk_hitboxes.c.obj'),('health_unit','/bankc1_part1d_v2.c.obj')]:
    rows=[r for r in db if r.get('output','').replace('\\','/').endswith(suffix) and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(rows)==1,(label,len(rows));cmd=argv(rows[0]['command']);tasks.append((label,cmd,(cwd/cmd[cmd.index('-c')+1]).resolve(),False))
for label,template,source,added in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d')),('-c',source)):cmd[cmd.index(flag)+1]=str(value)
    if label=='host':
        i=next(i for i,x in enumerate(cmd) if x.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    if added:inputs.append(obj.as_posix())
    else:
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old);inputs[indices[0]]=obj.as_posix()
    compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))};retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(linked)-len(tasks)
paths=[Path(__file__),bp,rsp,hunk,*[source for _,_,source,_ in tasks],*[ROOT/name for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','engine/runner/tlk_hitbox_data.h','engine/runner/tlk_md_sprite_format.inc','engine/runner/tlk_graveyard_gameplay.h','engine/runner/aot_pace.h','engine/generated/resources/pride_hitbox_map.h','engine/cmake/TlkPrideFinalPlayer.cmake')]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',digest(out/'player.exe'),flush=True)
