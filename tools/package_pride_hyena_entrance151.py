"""Stage the entrance-window player for default imported-data verification."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
proofs=[base/p/'report.json' for p in ('routes156-qualification','parent-verification','windows-ui','fights144-qualification')]
proofs += [ROOT/'build'/p/'report.json' for p in ('pride-hyena-entrance132','pride-hyena-countdown133')]
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
previous=ROOT/'dist/installed-preview118';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview139';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256']
info['hyena_entrance_window_scope']='Independent Pride entrance camera-window width: original MD320 pixels or native256, native audio synchronization and other AI retained; changing source restarts level'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text('Lion King Windows development preview139\n\nSetup.cmd prepares game data from your ROMs. F12 opens the resource tree.\nGameplay > Levels > Pride Lands > Hyena entrance countdown window selects\nthe original MD320-pixel window or original SNES256-pixel window. Changing it\nrestarts the level; camera, viewport, artwork and audio remain independent.\n\nRetains independent walking wall-probe height and corrected group inheritance.\nCompiled game code and remaining emulated routines/hardware are used.\nFull first-level fidelity work continues. Current-build saves only.\nNo ROMs or extracted game assets are bundled. See licenses.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';s=launcher.read_text();assert s.count('dist/installed-preview118')==1
candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists()
candidate.write_text(s.replace('dist/installed-preview118','dist/installed-preview139').replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
paths=[Path(__file__),bp,*proofs,old,launcher,candidate]
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,full_release_gates_required=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('STAGED',b['binary_sha256'],flush=True)
