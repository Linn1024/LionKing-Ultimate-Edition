"""Build prepared adult life portrait and common Hakuna/Destiny HUD artwork."""
import json,subprocess,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
bp=ROOT/'build/hakuna823/build-report.json';b=bound(bp);out=ROOT/'build/hakuna829';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(bp.parent/'link.rsp').read_text())[1:];compiles=dict(b['compiles']);db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd));row=next(r for r in db if r.get('output','').replace('\\','/').endswith('/game/tlk_md_hud.c.obj') and 'tlk_pride_final_player_' in r.get('output',''))
for label,cmd,src in [('wide',b['compiles']['wide'],None),('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('hud',argv(row['command']),out/'game/tlk_md_hud.c')]:
 cmd=cmd.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
 for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
 if src:cmd[cmd.index('-c')+1]=str(src)
 ix=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(ix)==1,(label,old)
 with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
 inputs[ix[0]]=obj.as_posix();compiles[label]=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(bp.parent/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll');paths=[Path(__file__),bp,rsp,*[ROOT/'engine/runner'/p for p in ('tlk_md_hud.c','tlk_md_hud.h','tlk_wide.c','tlk_resources.c')],out/'game/tlk_md_hud.c']
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',flush=True)
