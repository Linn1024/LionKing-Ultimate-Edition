"""Publish the focused battle cue change, retaining all installed asset packages."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-battle319/build-report.json';b=bound(build)
proof=ROOT/'build/pride-battle320/report.json';r=bound(proof);assert r['result']=='PASS'
window=ROOT/'build/pride-battle321-window/report.json';w=bound(window)
assert w['checks']['exit'] and w['checks']['real_window'] and w['checks']['compiled_interpreter_pcm']
assert len(w['jump'])==1 and all(w['jump'][0][key]==value for key,value in dict(pc='c144d8',music_track='134',active='1',audio_wait='0').items())
previous=ROOT/'dist/installed-preview307';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview319';out.mkdir(exist_ok=True)
for path in previous.rglob('*'):
    if not path.is_file() or path.name in ('package-report.json','package.json','LionKing.exe','README.txt'):continue
    target=out/path.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
shutil.copy2(build.parent/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256']
info['pride_battle_music_scope']='MD program134 starts at actual native opening jump, retaining native waits/movement. Sampled AOT/LLE command and PCM agree; audible-onset equivalence to original MD is not claimed.'
info['current_base_audio_history_schema']=3
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text().replace('preview307','preview319')+'\nMD Pride battle music now follows the actual opening jump. Original native\nwait and gameplay remain intact. Older development audio saves are unsupported.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text();assert text.count('dist/installed-preview307')==1
text=text.replace('dist/installed-preview307','dist/installed-preview319')
(build.parent/'RunInstalledPreview.publish.ps1').write_text(text)
candidate=build.parent/'RunInstalledPreviewCandidate.ps1';candidate.write_text(text.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
paths=[Path(__file__),build,proof,window,old,launcher,candidate]
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,window_qualification='Actual client inspected; cold replay issues program134 at its observed opening jump with wait0. The polled-input replay cursor is not resumed, so field3853 and whole guest differ from uninterrupted field3852. No cold replay equivalence claim; unrelated replay/save work deferred.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='package-report.json'}),indent=2)+'\n')
print('PACKAGED',b['binary_sha256'])
