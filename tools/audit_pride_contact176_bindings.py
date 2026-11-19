"""Bind refreshed current contact evidence without declaring full-level fidelity."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride-contact176-bindings';out.mkdir();checks={};paths=[Path(__file__)]
for name,expected in [('pride-contact166-observer/build-report.json','BUILT'),('pride-contact170-current/report.json','CAPTURED'),('pride-contact171-comparison/report.json','PASS'),('pride-contact172-modes/report.json','PASS'),('pride-contact173-window/report.json','PASS'),('pride-contact174-md-qualification/report.json','PASS'),('pride-hyena-entrance139/bindings/report.json','PASS')]:
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name]=r['result']==expected and all(r.get('checks',{}).values())
for name,expected in [('pride-contact167-current/attempt-report.json','FAIL'),('pride-contact168-md/report.json','DIFFERENCES')]:
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name+'_retained']=r['result']==expected
bp=ROOT/'build/pride-hyena-entrance139/build-report.json';b=bound(bp);paths.append(bp)
checks['published139_binary_exact']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==digest(bp.parent/'player.exe')==b['binary_sha256']
checks['all324_published_inputs_unchanged']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
checks['public_launcher_still139']='dist/installed-preview139' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
paths += list((ROOT/'tools').glob('*pride_contact*.py'))
paths += [ROOT/p for p in ('docs/HANDOFF.md','docs/pride-contact-current.md','docs/pride-actor-bounds.md','docs/pride-enemy-activation.md','docs/pride-lands-status.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','tools/pride_movement_audit.py','tools/compare_pride_roll_originals.py','tools/compare_pride_movement.py')]
paths += [ROOT/p for p in b['link_inputs_sha256']]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,current_player_sha256=b['binary_sha256'],samples_per_version=1238,
    full_first_level_complete=False,new_gameplay_or_capability_changes=False,scope='Fresh current139 bounded rolling/contact state/media/Windows verification. Raw failures and reference diagnostic additions retained. No full AI/difficulty/effect coverage or old-build save compatibility claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
