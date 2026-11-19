"""Record publication and precise reused regression provenance, without reruns."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-menu266-bindings';out.mkdir();checks={};paths=[Path(__file__)]
for folder,expected in (
    ('pride-menu245-allbugs','PASS'),('pride-menu246-md-timing','PASS'),('pride-menu247-md-pixels','PASS'),
    ('pride-menu248-native-routes','PASS'),('pride-menu249-native-gameover','PASS'),
    ('pride-menu250-parents/verified','PASS'),('pride-menu251-md-routes','FAIL'),
    ('pride-menu253-native256','PASS'),('pride-menu254-assets','PASS'),('pride-menu256-md-save','PASS'),
    ('pride-menu257-md-source-ui','PASS'),('pride-menu258-completion','PASS'),
    ('pride-menu261-help-ui','PASS'),('pride-menu262-md-routes','PASS'),
    ('pride-menu264-package','PASS'),('pride-menu265-publication','PASS')):
    p=ROOT/'build'/folder/'report.json';r=bound(p);paths.append(p)
    checks[folder]=r['result']==expected and (expected!='PASS' or all(r['checks'].values()))
for name in ('pride-menu226-integrated/native75/report.json','pride-menu243-bindings/report.json'):
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name]=r['result']=='PASS'
bp=ROOT/'build/pride-menu260-help/build-report.json';b=bound(bp);paths.append(bp)
checks['help_only_rebuild_retains_host_and323_inputs']=b['changes_only_help_string'] and b['inputs_retained']==323
checks['packaged_binary_exact']=digest(ROOT/'dist/installed-preview260/LionKing.exe')==b['binary_sha256']
checks['shared_launcher_selects260']='dist/installed-preview260' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
paths += [ROOT/p for p in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-menu-current-checks.md','docs/pride-final-menu-source.md','docs/background-audit.md','docs/launchers.md','README.md','engine/docs/devlog.md','engine/runner/tlk_resources.c','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    published=True,current_public_sha256=b['binary_sha256'],full_first_level_complete=False,
    regression_provenance='Full native75 and All Bugs on226.260 exact one-help-string resource-source diff and323 retained link objects including identical host; focused actual help and installed-window checks. No new260 full-suite claim.',
    scope='Current identity binding only, no game launches or regression reruns. User priority: implement remaining first-level behaviors and use focused, less frequent tests. Broad suites reserved for shared-engine changes or meaningful release milestones.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
