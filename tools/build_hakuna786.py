"""Build Hakuna/Destiny background adapters and saved waterfall/camera history."""
import json,subprocess,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
bp=ROOT/'build/next771/build-report.json';b=bound(bp);base=bp.parent
out=ROOT/'build/hakuna786';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
save=json.loads((ROOT/'build/pride-continue-token-behavior50/build-report.json').read_text())['compiles']['savestate']
for label,cmd,src in [('wide',b['compiles']['wide'],None),('assets',b['compiles']['assets'],ROOT/'engine/runner/tlk_md_assets.c'),('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('savestate',save,out/'game/tlk_savestate.c')]:
 cmd=cmd.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
 for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
 if src:cmd[cmd.index('-c')+1]=str(src)
 with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
 ix=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(ix)==1,(label,old);inputs[ix[0]]=obj.as_posix();compiles[label]=cmd
 print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
paths=[Path(__file__),bp,rsp,*[ROOT/'engine/runner'/p for p in ('tlk_md_assets.c','tlk_md_assets.h','tlk_md_assets_cache.inc','tlk_wide.c','tlk_wide.h','tlk_resources.c','tlk_savestate.c')],out/'game/tlk_savestate.c',out/'game/tlk_resources.c']
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('BUILT',flush=True)
