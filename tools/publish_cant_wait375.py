"""Publish prepared second-level foreground after focused installed checks."""
import json, os, shutil, subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

build=ROOT/'build/cant-wait372/build-report.json'; b=bound(build)
proofs=[ROOT/'build/cant-wait373/report.json',ROOT/'build/cant-wait374-window/report.json']
for p in proofs: assert bound(p)['result']=='PASS'
helper=ROOT/'build/cant-wait371-cmake/build-report.json'; h=bound(helper)
previous=ROOT/'dist/installed-preview362'; out=ROOT/'dist/installed-preview372'
out.mkdir(exist_ok=True)
for p in previous.rglob('*'):
    if p.is_file() and p.name not in ('package-report.json','package.json','README.txt','LionKing.exe'):
        target=out/p.relative_to(previous); target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text()); info['player_sha256']=b['binary_sha256']
info['cant_wait_foreground_scope']='Prepared MD foreground: 12391/12400 geometry-safe cells; nine cells retain native artwork. Collision and gameplay unchanged. Independent scenery/palette selections.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text()+'\nPreview372 adds prepared MD foreground artwork for Cant Wait to Be King.\nNine unmatched cells retain native art; gameplay/collision are unchanged.\n')
publication=ROOT/'build/cant-wait375-publication'; publication.mkdir(exist_ok=True)
launcher=ROOT/'scripts/RunInstalledPreview.ps1'; before=launcher.read_text()
assert before.count('dist/installed-preview362')==1
after=before.replace('dist/installed-preview362','dist/installed-preview372')
candidate=publication/'RunInstalledPreviewCandidate.ps1'
candidate.write_text(after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(candidate),'-DataDirectory',str(ROOT/'build/cant-wait371-setup'),'-SettingsDirectory',str(publication/'candidate-settings'),'-Frames','1','-NoPace','-NoAudio']
with (publication/'candidate.log').open('wb') as log: subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert 'native_hud_assets=loaded' in (publication/'candidate-settings/last-launch.log').read_text()
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('game-data','settings') for p in (ROOT/folder).rglob('*') if p.is_file()}
manifest=ROOT/'game-data/install.json'
if not (publication/'previous-install.json').exists(): shutil.copy2(manifest,publication/'previous-install.json')
old_manifest=json.loads((publication/'previous-install.json').read_text(encoding='utf-8-sig'))
shutil.copy2(launcher,publication/'previous-launcher.ps1')
helper_binary=ROOT/'build/cant-wait371-cmake/build/PrepareSceneAssets.exe'
assert digest(helper_binary)==h['binary_sha256']
installed_helper=ROOT/'dist/PrepareSceneAssets.exe'
if installed_helper.exists(): shutil.copy2(installed_helper,publication/'previous-PrepareSceneAssets.exe')
shutil.copy2(helper_binary,installed_helper)
setup=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(ROOT/'game-data'/old_manifest['roms']['snes']['file']),'-MdRom',str(ROOT/'game-data'/old_manifest['roms']['megadrive']['file']),'-DataDirectory',str(ROOT/'game-data')]
with (publication/'setup.log').open('wb') as log: subprocess.run(setup,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
current=json.loads(manifest.read_text(encoding='utf-8-sig'))
assert current['scene_cache']['sha256']==h['cache_sha256']
assert all(digest(ROOT/name)==sha for name,sha in protected.items() if name not in ('game-data/install.json','game-data/setup-last.log'))
for key,value in old_manifest.items():
    if isinstance(value,dict) and key!='scene_cache': assert current[key]==value, key
assert launcher.read_text()==before
launcher.write_text(after)
paths=[Path(__file__),build,helper,*proofs,launcher,ROOT/'scripts/Setup.ps1',manifest]
checks=dict(candidate_installed_launch=True,native_setup_completed=True,existing_data_and_settings_preserved=True,prepared_scene_selected=True)
artifacts={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED',published=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256=artifacts),indent=2)+'\n')
(publication/'report.json').write_text(json.dumps(dict(result='PASS',published=True,full_first_level_complete=False,checks=checks,command=cmd,setup_command=setup,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(publication).as_posix():digest(p) for p in publication.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks)
