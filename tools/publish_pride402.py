"""Publish the available-MD draft preset without changing installed data."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride398/build-report.json';b=bound(build)
proof=ROOT/'build/pride401-ui/report.json';assert bound(proof)['result']=='PASS'
previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398';out.mkdir(exist_ok=True)
for p in previous.rglob('*'):
    if p.is_file() and p.name not in ('package-report.json','package.json','README.txt','LionKing.exe'):
        target=out/p.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256']
info['available_md_preset_scope']='Resource editor MD/F7 drafts every currently available MD choice with inherited branches, explicit SNES overrides for unavailable leaves, individual overrides and ordinary Apply/restart. Existing settings/data unchanged until user applies.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text()+'\nPreview398: Resources > MD (or F7 in the SDL editor) drafts all available MD\nchoices. Unsupported choices remain SNES. Edit individual nodes, then Apply.\n')
publication=ROOT/'build/pride402-publication';publication.mkdir(exist_ok=True)
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview390')==1
after=before.replace('dist/installed-preview390','dist/installed-preview398')
candidate=publication/'RunInstalledPreviewCandidate.ps1';candidate.write_text(after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('game-data','settings') for p in (ROOT/folder).rglob('*') if p.is_file()}
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(candidate),'-SettingsDirectory',str(publication/'candidate-settings'),'-Frames','1','-NoPace','-NoAudio']
with (publication/'candidate.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert 'native_hud_assets=loaded' in (publication/'candidate-settings/last-launch.log').read_text()
assert all(digest(ROOT/name)==sha for name,sha in protected.items())
assert digest(out/'LionKing.exe')==b['binary_sha256'] and launcher.read_text()==before
shutil.copy2(launcher,publication/'previous-launcher.ps1');launcher.write_text(after)
paths=[Path(__file__),build,proof,launcher]
checks=dict(candidate_installed_launch=True,installed_data_and_settings_unchanged=True,verified_executable_selected=True)
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED',published=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}),indent=2)+'\n')
(publication/'report.json').write_text(json.dumps(dict(result='PASS',published=True,full_first_level_complete=False,checks=checks,command=cmd,protected_sha256=protected,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(publication).as_posix():digest(p) for p in publication.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks)
