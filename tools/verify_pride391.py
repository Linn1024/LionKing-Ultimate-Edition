"""Verify table preservation, unchanged artwork payload and actual Setup."""
import json,os,subprocess,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride390/build-report.json';bound(build)
helper=ROOT/'build/pride389-cmake/build-report.json';h=bound(helper)
out=ROOT/'build/pride391';out.mkdir(exist_ok=True)
sources=[ROOT/'tools/check_pride391_tables.c',build.parent/'game/tlk_md_sprites.c']+[ROOT/'engine/runner'/('tlk_'+name+'.c') for name in ('pride_data','start_data','reactivation_data','hitbox_data','roar_data','md_assets','contact_map')]+[ROOT/'engine/snesrecomp/runner/src/sha256.c']
cmd=['C:/mingw32/bin/gcc.exe','-O2','-static','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/generated/resources'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),*map(str,sources),'-o',str(out/'check.exe')]
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,check=True,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
roms=[ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md'];check=[str(out/'check.exe'),*map(str,roms),str(helper.parent/'sprites.assets')]
result=subprocess.check_output(check,cwd=ROOT,text=True);(out/'check.log').write_text(result)
manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
old=(ROOT/'game-data'/manifest['sprite_assets']['file']).read_bytes();new=(helper.parent/'sprites.assets').read_bytes()
payload_same=old[192:]==new[192:len(old)] and old[20:120]==new[20:120] and old[152:164]==new[152:164]
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
setup=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(roms[0]),'-MdRom',str(roms[1]),'-DataDirectory',str(out/'data'),'-SpritePreparer',str(helper.parent/'build/PrepareSpriteAssets.exe')]
with (out/'setup.log').open('wb') as log:subprocess.run(setup,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
m=json.loads((out/'data/install.json').read_text(encoding='utf-8-sig'))
checks=dict(original_tables_equal_installed_activation=result.startswith('PASS '),artwork_palettes_policy_unchanged=payload_same,sprite_v2=m['sprite_assets']['version']==2,actual_setup_package=m['sprite_assets']['sha256']==h['cache_sha256'],scene_package_unchanged=m['scene_cache']==manifest['scene_cache'])
paths=[Path(__file__),ROOT/'tools/check_pride391_tables.c',build,helper,ROOT/'scripts/Setup.ps1',out/'data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,compile_command=cmd,check_command=check,setup_command=setup,scope='Original init versus installed activation for all four tables, four malformed-section transactional rejections, previous artwork/palettes/policy exact; actual Setup uses sprite-v2 and preserves scene-v2.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'check.log':digest(out/'check.log'),'setup.log':digest(out/'setup.log')}),indent=2)+'\n')
print(result.strip(),checks,flush=True)
