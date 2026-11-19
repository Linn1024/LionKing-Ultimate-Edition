"""Run actual Setup with the new native sprite preparer in an isolated data directory."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
helper=ROOT/'build/cant-wait459-helper/build-report.json';h=bound(helper)
build=ROOT/'build/cant-wait460/build-report.json';bound(build)
out=ROOT/'build/cant-wait464-setup';out.mkdir(exist_ok=True)
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(ROOT/'Lion King, The (USA).sfc'),'-MdRom',str(ROOT/'Lion King, The (World).md'),'-DataDirectory',str(out/'data'),'-SpritePreparer',str(helper.parent/'build/PrepareSpriteAssets.exe')]
with (out/'setup.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
m=json.loads((out/'data/install.json').read_text(encoding='utf-8-sig'));current=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
checks=dict(native_setup_output=m['sprite_assets']['sha256']==h['cache_sha256'],sprite_version_retained=m['sprite_assets']['version']==2,other_payloads_unchanged=all(m[k]==v for k,v in current.items() if isinstance(v,dict) and k!='sprite_assets'))
paths=[Path(__file__),helper,build,ROOT/'scripts/Setup.ps1',out/'data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print(checks,flush=True)
