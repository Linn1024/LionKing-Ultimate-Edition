"""Publish bundled prepared gameplay data after focused route/window checks."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride390/build-report.json';b=bound(build)
proofs=[ROOT/'build/pride391/report.json',ROOT/'build/pride392-route/report.json',ROOT/'build/pride394-qualification/report.json']
for p in proofs:assert bound(p)['result']=='PASS'
helper=ROOT/'build/pride389-cmake/build-report.json';h=bound(helper)
previous=ROOT/'dist/installed-preview382';out=ROOT/'dist/installed-preview390';out.mkdir(exist_ok=True)
for p in previous.rglob('*'):
    if p.is_file() and p.name not in ('package-report.json','package.json','README.txt','LionKing.exe'):
        target=out/p.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256'];info['required_sprite_assets_version']=2
info['prepared_pride_gameplay_scope']='Sprite-v2 includes both default start positions, lizard reactivation flags,836 pose hitboxes and14 roar tokens/fire delay. Installed playback imports these tables; gameplay algorithms, artwork and source choices unchanged.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text()+'\nPreview390 loads Pride start/reactivation/hitbox/roar tables from Setup.\nRequires sprite-v2 and scene-v2 packages; settings are preserved.\n')
publication=ROOT/'build/pride395-publication';publication.mkdir(exist_ok=True)
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview382')==1
after=before.replace('dist/installed-preview382','dist/installed-preview390').replace('Resolve-PreparedFile $manifest.sprite_assets 1','Resolve-PreparedFile $manifest.sprite_assets 2')
assert 'Resolve-PreparedFile $manifest.sprite_assets 2' in after
candidate=publication/'RunInstalledPreviewCandidate.ps1';candidate.write_text(after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(candidate),'-DataDirectory',str(ROOT/'build/pride391/data'),'-SettingsDirectory',str(publication/'candidate-settings'),'-Frames','1','-NoPace','-NoAudio']
with (publication/'candidate.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert 'native_hud_assets=loaded' in (publication/'candidate-settings/last-launch.log').read_text()
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('game-data','settings') for p in (ROOT/folder).rglob('*') if p.is_file()}
manifest=ROOT/'game-data/install.json';old=json.loads(manifest.read_text(encoding='utf-8-sig'))
shutil.copy2(manifest,publication/'previous-install.json');shutil.copy2(launcher,publication/'previous-launcher.ps1')
helper_binary=ROOT/'build/pride389-cmake/build/PrepareSpriteAssets.exe';assert digest(helper_binary)==h['binary_sha256']
installed_helper=ROOT/'dist/PrepareSpriteAssets.exe';shutil.copy2(installed_helper,publication/'previous-PrepareSpriteAssets.exe');shutil.copy2(helper_binary,installed_helper)
setup=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(ROOT/'game-data'/old['roms']['snes']['file']),'-MdRom',str(ROOT/'game-data'/old['roms']['megadrive']['file']),'-DataDirectory',str(ROOT/'game-data')]
with (publication/'setup.log').open('wb') as log:subprocess.run(setup,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
current=json.loads(manifest.read_text(encoding='utf-8-sig'))
assert current['sprite_assets']['version']==2 and current['sprite_assets']['sha256']==h['cache_sha256']
assert all(digest(ROOT/name)==sha for name,sha in protected.items() if name not in ('game-data/install.json','game-data/setup-last.log'))
for key,value in old.items():
    if isinstance(value,dict) and key!='sprite_assets':assert current[key]==value,key
assert digest(out/'LionKing.exe')==b['binary_sha256'] and launcher.read_text()==before
launcher.write_text(after)
paths=[Path(__file__),build,helper,*proofs,launcher,ROOT/'scripts/Setup.ps1',manifest]
checks=dict(candidate_installed_launch=True,actual_native_setup=True,other_packages_preserved=True,existing_assets_and_settings_preserved=True,prepared_sprite_v2_selected=True)
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED',published=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}),indent=2)+'\n')
(publication/'report.json').write_text(json.dumps(dict(result='PASS',published=True,full_first_level_complete=False,checks=checks,command=cmd,setup_command=setup,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(publication).as_posix():digest(p) for p in publication.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks)
