"""Publish coherent Hakuna/Destiny player, native preparers and installed resources."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
proof=ROOT/'build/later917-qualified/report.json';q=bound(proof);assert q['result']=='PASS'
build=ROOT/'build/later910/build-report.json';b=bound(build);scene=ROOT/'build/hakuna787-helper/build-report.json';sh=bound(scene);sprite=ROOT/'build/later909-helper/build-report.json';sp=bound(sprite)
previous=ROOT/'dist/installed-preview849';out=ROOT/'dist/installed-preview910';out.mkdir(exist_ok=True);publication=ROOT/'build/later918-publication';publication.mkdir(exist_ok=True)
for p in previous.rglob('*'):
 if p.is_file() and p.name not in ('LionKing.exe','package.json','package-report.json','README.txt'):
  target=out/p.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info.update(player_sha256=b['binary_sha256'],required_scene_cache_version=3,required_sprite_assets_version=2,required_sprite_policy_sha256=(sprite.parent/'sprites.assets').read_bytes()[88:120].hex(),wide_history_schema=6,be_prepared_return_scope=q['scope'])
info['required_packages']['scene_cache']=3;info['required_packages']['sprite_assets']=2
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n');(out/'README.txt').write_text('Lion King development preview910\n\nLaunch Play Be Prepared MD.cmd or Play Simbas Return MD.cmd.\nExisting settings are preserved; new shortcuts have separate defaults.\nSetup prepares scene-v3 and sprite-v2 policy7 resources. HUD cache-v1 remains valid.\n\n'+q['scope']+'\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview849')==1
after=before.replace('dist/installed-preview849','dist/installed-preview910').replace('Resolve-PreparedFile $manifest.scene_cache 2','Resolve-PreparedFile $manifest.scene_cache 3')
assert 'Resolve-PreparedFile $manifest.scene_cache 3' in after
candidate=publication/'RunInstalledPreviewCandidate.ps1';candidate.write_text(after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe');cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(candidate),'-DataDirectory',str(ROOT/'build/later916-setup/data'),'-SettingsDirectory',str(publication/'candidate-settings'),'-Frames','1','-NoPace','-NoAudio']
with (publication/'candidate.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
candidate_log=(publication/'candidate-settings/last-launch.log').read_text()
assert 'resource_cache=loaded' in candidate_log and 'native_hud_assets=loaded' in candidate_log
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('settings','game-data') for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}
manifest=ROOT/'game-data/install.json';old=json.loads(manifest.read_text(encoding='utf-8-sig'));shutil.copy2(manifest,publication/'previous-install.json');shutil.copy2(launcher,publication/'previous-launcher.ps1')
for name,helper,h in [('PrepareSceneAssets.exe',scene,sh),('PrepareSpriteAssets.exe',sprite,sp)]:
 binary=helper.parent/'build'/name;assert digest(binary)==h['binary_sha256'];target=ROOT/'dist'/name;shutil.copy2(target,publication/('previous-'+name));shutil.copy2(binary,target)
setup=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(ROOT/'game-data'/old['roms']['snes']['file']),'-MdRom',str(ROOT/'game-data'/old['roms']['megadrive']['file']),'-DataDirectory',str(ROOT/'game-data')]
with (publication/'setup.log').open('wb') as log:subprocess.run(setup,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=65,creationflags=subprocess.CREATE_NO_WINDOW)
current=json.loads(manifest.read_text(encoding='utf-8-sig'));assert current['scene_cache']['version']==3 and current['scene_cache']['sha256']==sh['cache_sha256'];assert current['sprite_assets']['sha256']==sp['cache_sha256']
assert all(digest(ROOT/name)==sha for name,sha in protected.items() if name not in ('game-data/install.json','game-data/setup-last.log'))
for key,value in old.items():
 if isinstance(value,dict) and key not in ('scene_cache','sprite_assets'):
  assert current[key]==value if key=='roms' else current[key]['sha256']==value['sha256'],key
assert launcher.read_text()==before;launcher.write_text(after)
paths=[Path(__file__),proof,build,scene,sprite,launcher,ROOT/'scripts/Setup.ps1',manifest]
checks=dict(candidate_launch=True,actual_native_setup=True,coherent_scene_and_sprite_versions=True,other_payloads_preserved=True,existing_settings_and_assets_preserved=True)
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED',published=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}),indent=2)+'\n')
(publication/'report.json').write_text(json.dumps(dict(result='PASS',published=True,checks=checks,scope=q['scope'],command=cmd,setup_command=setup,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PUBLISHED',b['binary_sha256'],checks,flush=True)
