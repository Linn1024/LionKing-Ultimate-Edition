"""Package and select independent porcupine voice timing; no asset reinstall."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-porcupine327/build-report.json';b=bound(build)
proof=ROOT/'build/pride-porcupine329-baseline/report.json';assert bound(proof)['result']=='PASS'
window=ROOT/'build/pride-porcupine330-window/report.json';assert bound(window)['result']=='PASS'
previous=ROOT/'dist/installed-preview319';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview327';out.mkdir(exist_ok=True)
for path in previous.rglob('*'):
    if not path.is_file() or path.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    target=out/path.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256']
info['pride_porcupine_voice_scope']='Selected MD FM105 at original counter28 seam under either attack-contact timing source; native sound follows selected gameplay cue. Existing native cue interception retained; no new guest writes or save state.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text().replace('preview319','preview327')+'\nSelected MD porcupine attack sound now uses original counter28 timing,\nindependently of attack contact timing. Installed assets/settings are retained.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview319')==1
after=before.replace('dist/installed-preview319','dist/installed-preview327')
candidate=build.parent/'RunInstalledPreviewCandidate.ps1';candidate.write_text(after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
package=out/'package-report.json';paths=[Path(__file__),build,proof,window,old,candidate,launcher]
package.write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}),indent=2)+'\n')
publication=ROOT/'build/pride-porcupine331-publication';publication.mkdir(exist_ok=True)
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('game-data','settings') for p in (ROOT/folder).rglob('*') if p.is_file()}
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(candidate),'-SettingsDirectory',str(publication/'candidate-settings'),'-Frames','1','-NoPace','-NoAudio']
with (publication/'candidate.log').open('wb') as log:subprocess.run(cmd,cwd=publication,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert 'native_hud_assets=loaded' in (publication/'candidate-settings/last-launch.log').read_text()
assert all(digest(ROOT/name)==sha for name,sha in protected.items())
assert digest(out/'LionKing.exe')==b['binary_sha256'];assert launcher.read_text()==before;launcher.write_text(after)
checks=dict(candidate_installed_launch=True,installed_data_and_settings_preserved=True,verified_executable_selected=True)
paths=[Path(__file__),build,proof,window,package,launcher,ROOT/'build/pride-porcupine326-baseline/report.json']
(publication/'report.json').write_text(json.dumps(dict(result='PASS',checks=checks,published=True,full_first_level_complete=False,command=cmd,protected_sha256=protected,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'candidate.log':digest(publication/'candidate.log')}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks)
