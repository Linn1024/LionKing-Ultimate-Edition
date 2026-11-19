"""Build required installed caption playback and its native preparation helper."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-caption268';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-caption277-installed';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
original=cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
for patches,src,target in (('game-patches',ROOT/'engine',out/'game'),('final-frontend-patches',original,out/'frontend')):
    with (out/(patches+'.log')).open('wb') as log:
        subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake'/patches),'--snesrecomp',str(src),'--out',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(original/name,out/'frontend'/name)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
for label,src in (('host',ROOT/'engine/runner/pride/final/pride_final_host.c'),('resources',out/'game/tlk_resources.c')):
    cmd=b['compiles'][label].copy();old=(cwd/Path(cmd[cmd.index('-o')+1])).resolve();obj=out/(label+'.obj')
    for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    if label=='host':
        i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd
obj=out/'title-art.obj';cmd=['C:/mingw32/bin/gcc.exe','-O3','-std=gnu11','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),'-c',str(ROOT/'engine/runner/tlk_title_art.c'),'-o',str(obj)]
subprocess.run(cmd,check=True);compiles['caption_reader']=cmd
indices=[i for i,p in enumerate(inputs) if p.replace('\\','/').endswith('/libtlk_title_art.a')];assert len(indices)==1
inputs[indices[0]]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
helper=ROOT/'build/pride-caption276-helper/tlk_prepare_caption_assets.exe'
subprocess.run([str(helper),'--snes-rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--output',str(out/'captions.assets')],check=True)
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
paths=[Path(__file__),bp,helper,rsp,out/'frontend/sdl_main.c',out/'game/tlk_resources.c',*[ROOT/'engine/runner'/p for p in ('tlk_title_art.c','tlk_title_art.h','tlk_title_art_assets.inc','tlk_resources.c','tlk_resources.h','pride/final/pride_final_host.c')],ROOT/'engine/cmake/final-frontend-patches/presentation.hunks',ROOT/'engine/tools/prepare_caption_assets.c',ROOT/'engine/cmake/TlkCaptionAssets.cmake']
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=321,caption_package_sha256=digest(out/'captions.assets'),
    scope='Installed caption reader replaces startup title-art ROM extraction. Requires --caption-assets; explicit Setup error, no decoder fallback. Original extraction compiled into installer only. Other startup components remain hybrid/migration work.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
