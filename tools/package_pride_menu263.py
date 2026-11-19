"""Package the verified independent menu source with the help-only260 update."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-menu260-help';bp=base/'build-report.json';b=bound(bp)
assert b['changes_only_help_string'] and b['inputs_retained']==323
assert digest(base/'player.exe')==b['binary_sha256']
proofs=[ROOT/'build'/p/'report.json' for p in ('pride-menu245-allbugs','pride-menu246-md-timing','pride-menu247-md-pixels','pride-menu248-native-routes','pride-menu249-native-gameover','pride-menu250-parents/verified','pride-menu253-native256','pride-menu254-assets','pride-menu257-md-source-ui','pride-menu258-completion','pride-menu261-help-ui','pride-menu262-md-routes')]
proofs.append(ROOT/'build/pride-menu226-integrated/native75/report.json')
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
previous=ROOT/'dist/installed-preview139';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview260';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256']
info['pride_final_menu_scope']='Independent installed Mega Drive Continue/Game Over artwork, palette and animation with SNES or MD final-life timing. Source edits restart level. Other levels retain native menus. Saving during native-timing MD-art menu episodes is unavailable.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text('Lion King Windows development preview260\n\nSetup.cmd prepares game data from your ROMs. F12 opens the resource tree.\nGraphics > Pride Lands Continue / Game Over selects SNES or Mega Drive menu\nartwork, palette and animation independently of transition timing and audio.\nChanging the artwork source restarts the level. Other levels keep native menus.\nSaving during native-timing MD-art final menu episodes is unavailable; resume\ngameplay before saving. Current-build saves only.\n\nRetains the preceding supported resource and gameplay choices. Full first-level\nfidelity remains in development. Compiled game code and emulated components\nare used. No ROMs or extracted game assets are bundled. See licenses.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';s=launcher.read_text();assert s.count('dist/installed-preview139')==1
candidate=base/'RunInstalledPreviewCandidate.ps1'
candidate.write_text(s.replace('dist/installed-preview139','dist/installed-preview260').replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
paths=[Path(__file__),bp,*proofs,old,launcher,candidate]
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,
    regression_provenance='226 full native75/All Bugs and focused menu/source/context proofs;260 exact help-string-only resource diff retains host and323/324 inputs. Long suites were not repeated for a description change.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PACKAGED',b['binary_sha256'],flush=True)
