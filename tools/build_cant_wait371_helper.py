"""Build the maintained native scene preparer through its shared CMake module."""
import json,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait371-cmake';out.mkdir(exist_ok=True)
(out/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\nproject(ScenePreparation C)\ninclude("'+(ROOT/'engine/cmake/TlkSceneAssets.cmake').as_posix()+'")\ntlk_add_scene_asset_preparer(PrepareSceneAssets)\n')
commands=[['cmake','-S',str(out),'-B',str(out/'build'),'-G','Ninja','-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe','-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(out/'build'),'--target','PrepareSceneAssets','-j','4']]
for i,cmd in enumerate(commands):
    with (out/('step'+str(i)+'.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
exe=out/'build/PrepareSceneAssets.exe';cmd=[str(exe),'--snes-rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--output',str(out/'scenes.cache')]
with (out/'prepare.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
paths=[Path(__file__),ROOT/'engine/cmake/TlkSceneAssets.cmake',ROOT/'engine/tools/prepare_scene_assets.c',ROOT/'engine/runner/tlk_md_assets.c',exe]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',commands=commands,prepare_command=cmd,binary_sha256=digest(exe),cache_sha256=digest(out/'scenes.cache'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print((out/'prepare.log').read_text(),flush=True)
