"""Build and run sprite-v2 preparation, including immutable gameplay tables."""
import json,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride389-cmake';out.mkdir(exist_ok=True)
(out/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.20)\nproject(PridePreparation C)\ninclude("'+(ROOT/'engine/cmake/TlkSpriteAssets.cmake').as_posix()+'")\ntlk_add_sprite_asset_preparer(PrepareSpriteAssets)\n')
commands=[['cmake','-S',str(out),'-B',str(out/'build'),'-G','Ninja','-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe','-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(out/'build'),'-j','4']]
for i,cmd in enumerate(commands):
    with (out/('step'+str(i)+'.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
exe=out/'build/PrepareSpriteAssets.exe';cmd=[str(exe),'--snes-rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--output',str(out/'sprites.assets')]
with (out/'prepare.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
names=['engine/runner/tlk_'+part+suffix for part in ('start_data','reactivation_data','hitbox_data','roar_data','pride_data') for suffix in ('.c','.h')]
names+=['engine/runner/tlk_data_record.h','engine/runner/tlk_md_sprite_prepare.c','engine/runner/tlk_md_sprite_format.inc','engine/cmake/TlkSpriteAssets.cmake']
paths=[Path(__file__),exe,*[ROOT/name for name in names]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',commands=commands,prepare_command=cmd,binary_sha256=digest(exe),cache_sha256=digest(out/'sprites.assets'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print((out/'prepare.log').read_text(),flush=True)
