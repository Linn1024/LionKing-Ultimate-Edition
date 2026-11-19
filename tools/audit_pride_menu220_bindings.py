"""Bind native256 Continue progress, retained attempts and unchanged public139."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride-menu220-bindings';out.mkdir();checks={};paths=[Path(__file__)]
reports={
    'pride-menu209-observer/build-report.json':'BUILT',
    'pride-menu210-continue/report.json':'CAPTURED',
    'pride-menu213-phases/build-report.json':'BUILT',
    'pride-menu214-phases/report.json':'PASS',
    'pride-menu215-native-art/build-report.json':'BUILT',
    'pride-menu216-continue/report.json':'PASS',
    'pride-menu217-windows/report.json':'PASS',
    'pride-menu218-pixels/report.json':'PASS',
    'pride-menu205-bindings/report.json':'PASS',
    'pride-hyena-entrance139/bindings/report.json':'PASS',
}
for name,expected in reports.items():
    p=ROOT/'build'/name;r=bound(p);paths.append(p)
    checks[name]=r['result']==expected and all(r.get('checks',{}).values())
    if expected=='BUILT':
        checks[name+'_binary_exact']=digest(p.parent/'player.exe')==r['binary_sha256']
        checks[name+'_all324_link_inputs_exact']=len(r['link_inputs_sha256'])==324 and all(digest(ROOT/q)==sha for q,sha in r['link_inputs_sha256'].items())
for name in ('pride-menu206-observer','pride-menu207-observer','pride-menu211-phases','pride-menu212-phases'):
    p=ROOT/'build'/name/'attempt-report.json';r=bound(p);paths.append(p);checks[name+'_failed_attempt_retained']=r['result']=='FAIL'
p=ROOT/'build/pride-menu208-observer/build-report.json';r=bound(p);paths.append(p)
checks['unused208_build_retained']=r['result']=='BUILT' and digest(p.parent/'player.exe')==r['binary_sha256']
bp=ROOT/'build/pride-hyena-entrance139/build-report.json';b=bound(bp);paths.append(bp)
checks['public139_binary_exact']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==digest(bp.parent/'player.exe')==b['binary_sha256']
checks['all324_public_link_inputs_unchanged']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
launcher=ROOT/'scripts/RunInstalledPreview.ps1'
checks['public_launcher_still139']='dist/installed-preview139' in launcher.read_text() and 'TLK_NATIVE_MENU215' not in launcher.read_text()
checks['capability_reports_native_menu_art']='native menu artwork' in (ROOT/'engine/runner/tlk_resources.c').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
paths += [ROOT/p for p in b['link_inputs_sha256']]
paths += [ROOT/p for p in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-native-continue.md',
    'docs/pride-final-menu-native-timing.md','docs/pride-final-menu-drawing.md','docs/pride-final-menu-layout.md',
    'docs/pride-final-menu-yes.md','docs/background-audit.md','engine/docs/devlog.md','tools/pride_arena_history.py',
    'tools/pride_menu215_native_art.inc','scripts/RunInstalledPreview.ps1','engine/runner/tlk_resources.c')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    current_player_sha256=b['binary_sha256'],full_first_level_complete=False,public_capability_or_gameplay_changed=False,
    scope='Private native256 MD-art Continue idle/YES/NO guest/audio/modes and actual complete Windows pixel proof. '
          'Retained failed tooling and unused208, unchanged public139 identities.320, GameOver regression on215 '
          'and source/restart/current-save integration remain required. Immediate prior bindings, not a new recursive release-gate run.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
