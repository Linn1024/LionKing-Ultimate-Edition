"""Bind width correction/staged integration without claiming release readiness."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride-menu231-bindings';out.mkdir();checks={};paths=[Path(__file__)]
for name,expected in (
    ('pride-menu221-wide/report.json','PASS'),('pride-menu222-game-over/report.json','PASS'),
    ('pride-menu223-wide-windows/report.json','PASS'),('pride-menu224-wide-pixels/report.json','FAIL'),
    ('pride-menu226-integrated/build-report.json','BUILT'),('pride-menu227-integrated-windows/report.json','PASS'),
    ('pride-menu228-corrected-pixels/report.json','PASS'),('pride-menu229-resource-ui/attempt-report.json','FAIL'),
    ('pride-menu220-bindings/report.json','PASS'),('pride-hyena-entrance139/bindings/report.json','PASS')):
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name]=r['result']==expected
    if expected=='PASS':checks[name] &= all(r.get('checks',{}).values())
    if expected=='BUILT':
        checks['staged226_binary_exact']=digest(p.parent/'player.exe')==r['binary_sha256']
        checks['all324_staged_inputs_exact']=len(r['link_inputs_sha256'])==324 and all(digest(ROOT/q)==sha for q,sha in r['link_inputs_sha256'].items())
        checks['only_host_resources_rebuilt']=r['inputs_retained']==322
bp=ROOT/'build/pride-hyena-entrance139/build-report.json';b=bound(bp);paths.append(bp)
checks['public139_binary_unchanged']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==digest(bp.parent/'player.exe')==b['binary_sha256']
checks['all324_public_inputs_unchanged']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
checks['launcher_still139']='dist/installed-preview139' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
paths += [ROOT/p for p in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-source.md',
    'docs/pride-final-menu-native-continue.md','docs/pride-final-menu-native-timing.md','docs/background-audit.md',
    'engine/docs/devlog.md','tools/pride_arena_history.py','tools/pride_process_read.py',
    'engine/runner/pride/final/pride_final_menu_native.inc','engine/runner/tlk_final_menu_policy.h',
    'engine/runner/tlk_resources.c','engine/cmake/TlkPrideFinalPlayer.cmake','scripts/RunInstalledPreview.ps1')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    current_public_sha256=b['binary_sha256'],full_first_level_complete=False,new_release_gates_complete=False,
    source_switch_restart_gate_complete=False,current_save_gate_complete=False,
    scope='Bindings only: retained width-pixel failure corrected in staged226 actual source-driven320 YES; failed UI restart harness retained. Public139 unchanged. Current source/lifecycle/save/full regression gates remain; critical disk request pending.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
