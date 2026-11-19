"""Check prepared contact/palette parity and actual Setup v2 output."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride379/build-report.json';bound(build)
helper=ROOT/'build/pride378-cmake/build-report.json';h=bound(helper)
out=ROOT/'build/pride380';out.mkdir(exist_ok=True)
cmd=['C:/mingw32/bin/gcc.exe','-O2','-static','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(ROOT/'tools/check_pride380_cache.c'),str(ROOT/'engine/runner/tlk_md_assets.c'),str(ROOT/'engine/runner/tlk_contact_map.c'),str(ROOT/'engine/snesrecomp/runner/src/sha256.c'),'-o',str(out/'check.exe')]
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,check=True,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
roms=[ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md']
cache=helper.parent/'scenes.cache';check=[str(out/'check.exe'),*map(str,roms),str(cache)]
result=subprocess.check_output(check,cwd=ROOT,text=True);(out/'check.log').write_text(result)
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
setup=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(roms[0]),'-MdRom',str(roms[1]),'-DataDirectory',str(out/'data'),'-ScenePreparer',str(helper.parent/'build/PrepareSceneAssets.exe')]
with (out/'setup.log').open('wb') as log:subprocess.run(setup,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
m=json.loads((out/'data/install.json').read_text(encoding='utf-8-sig'))
checks=dict(contact_and_palette_roundtrip=result.startswith('PASS cells=8000'),actual_setup_v2=m['scene_cache']['version']==2,prepared_cache_exact=m['scene_cache']['sha256']==h['cache_sha256'],all_contact_cells=m['scene_cache']['pride_contact_cells']==8000)
paths=[Path(__file__),ROOT/'tools/check_pride380_cache.c',build,helper,ROOT/'scripts/Setup.ps1',out/'data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,compile_command=cmd,check_command=check,setup_command=setup,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'check.log':digest(out/'check.log'),'setup.log':digest(out/'setup.log')}),indent=2)+'\n')
print(result.strip(),checks,flush=True)
