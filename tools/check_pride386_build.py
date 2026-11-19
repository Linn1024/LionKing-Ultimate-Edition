"""Check affected installer helper link dependencies without replaying gameplay."""
import json,subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride386-links';out.mkdir(exist_ok=True)
(out/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\nproject(PreparedSceneLinks C)\ninclude("'+(ROOT/'engine/cmake/TlkFinalAssets.cmake').as_posix()+'")\ninclude("'+(ROOT/'engine/cmake/TlkSpriteAssets.cmake').as_posix()+'")\ntlk_add_final_asset_preparer(PrepareFinalAssets)\ntlk_add_sprite_asset_preparer(PrepareSpriteAssets)\n')
commands=[['cmake','-S',str(out),'-B',str(out/'build'),'-G','Ninja','-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe','-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(out/'build'),'-j','4']]
for i,cmd in enumerate(commands):
    with (out/('step'+str(i)+'.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
paths=[ROOT/p for p in ('engine/CMakeLists.txt','engine/cmake/TlkFinalAssets.cmake','engine/cmake/TlkSpriteAssets.cmake','engine/cmake/TlkSceneAssets.cmake','engine/tests/md_assets_test.c','engine/tests/cant_wait_background_test.c')]
(out/'report.json').write_text(json.dumps(dict(result='PASS',scope='Affected native Final/Sprite helper targets compile and link with contact-map dependency. CMake test target dependencies and stale scene1/cache-v1 assertions updated; no unrelated test matrix run.',commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={name:digest(out/name) for name in ('build/PrepareFinalAssets.exe','build/PrepareSpriteAssets.exe')}),indent=2)+'\n')
print('PASS affected installer helper links')
