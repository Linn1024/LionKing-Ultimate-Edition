"""Stage current103 for installed-data verification; shared launcher remains86."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-probe103';bp=base/'build-report.json';build=bound(bp)
proofs=[base/'routes-qualification106/report.json',base/'fights104/report.json',base/'windows-ui-qualification104/report.json',ROOT/'build/pride-hyena-probe103-original/report.json',ROOT/'build/pride-hyena-probe103-component/report.json']
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
previous=ROOT/'dist/installed-preview86';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview103';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=build['binary_sha256']
info['hyena_walking_probe_scope']='Independent original MD walking wall query eight pixels higher; known Pride hyena main walking callers only; source changes restart level'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text('Lion King Windows development preview103\n\nSetup.cmd prepares game data from your ROMs. F12 opens the resource tree.\nGameplay > Levels > Pride Lands > Hyena walking wall-probe height selects\nthe original MD higher query or the original SNES query. Changing it restarts\nthe level; terrain map, body bounds, graphics and audio remain independent.\n\nCompiled game code and remaining emulated routines/hardware are used.\nFull first-level fidelity work continues. Current-build saves only.\nNo ROMs or extracted game assets are bundled. See licenses.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text();assert text.count('dist/installed-preview86')==1
candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists()
candidate.write_text(text.replace('dist/installed-preview86','dist/installed-preview103').replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
paths=[Path(__file__),bp,*proofs,old,launcher,candidate]
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,native75_and_allbugs_pending=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('STAGED',build['binary_sha256'],flush=True)
