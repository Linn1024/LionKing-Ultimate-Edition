"""Bind bounded all-difficulty porcupine evidence and unchanged public139."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out = ROOT / 'build/pride-porcupine196-bindings'
out.mkdir()
checks = {}
paths = [Path(__file__)]
positive = {
    'md-porcupine178-difficulty/report.json': 'CAPTURED',
    'pride-damage184-observer/build-report.json': 'BUILT',
    'pride-porcupine186-polled/report.json': 'CAPTURED',
    'pride-porcupine187-difficulty/report.json': 'PASS',
    'pride-porcupine188-modes/report.json': 'PASS',
    'md-porcupine189-neutral/report.json': 'PASS',
    'pride-porcupine190-windows/report.json': 'PASS',
    'pride-porcupine191-md-timing/report.json': 'CAPTURED',
    'pride-porcupine192-md-timing/report.json': 'PASS',
    'pride-porcupine193-md-modes/report.json': 'PASS',
    'pride-porcupine194-md-windows/report.json': 'PASS',
    'pride-contact176-bindings/report.json': 'PASS',
    'pride-hyena-entrance139/bindings/report.json': 'PASS',
}
negative = {
    'pride-porcupine177-difficulty/report.json': 'NO_ATTRIBUTED_HIT',
    'pride-porcupine179-shift-1/report.json': 'NO_ATTRIBUTED_HIT',
    'pride-porcupine179-shift1/report.json': 'NO_ATTRIBUTED_HIT',
    'pride-porcupine179-shift2/report.json': 'NO_ATTRIBUTED_HIT',
    'pride-porcupine181-ready-aligned/attempt-report.json': 'FAIL',
    'pride-porcupine183-actual-aligned/report.json': 'NO_ATTRIBUTED_HIT',
    'pride-porcupine185-roar/report.json': 'NO_PORCUPINE_HIT',
}
for name, expected in {**positive, **negative}.items():
    p = ROOT / 'build' / name
    report = bound(p)
    paths.append(p)
    checks[name] = report['result'] == expected
    if name in positive:
        checks[name] &= all(report.get('checks', {}).values())

bp = ROOT / 'build/pride-hyena-entrance139/build-report.json'
b = bound(bp)
paths.append(bp)
checks['published139_binary_exact'] = (
    digest(ROOT / 'dist/installed-preview139/LionKing.exe') ==
    digest(bp.parent / 'player.exe') == b['binary_sha256'])
checks['all324_published_inputs_unchanged'] = (
    len(b['link_inputs_sha256']) == 324 and
    all(digest(ROOT / p) == sha for p, sha in b['link_inputs_sha256'].items()))
checks['public_launcher_still139'] = 'dist/installed-preview139' in (
    ROOT / 'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean'] = not subprocess.check_output(
    ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'],
    cwd=ROOT / 'engine').strip()
paths += [ROOT / p for p in b['link_inputs_sha256']]
paths += [ROOT / p for p in (
    'docs/HANDOFF.md', 'docs/pride-lands-status.md',
    'docs/pride-porcupine-difficulty.md', 'docs/pride-porcupine-contacts.md',
    'docs/pride-porcupine-runtime.md', 'docs/pride-porcupine-applicability.md',
    'engine/docs/devlog.md', 'tools/pride_arena_history.py',
    'scripts/RunInstalledPreview.ps1')]
(out / 'report.json').write_text(json.dumps(dict(
    result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
    current_player_sha256=b['binary_sha256'],
    full_first_level_complete=False, gameplay_changes=False,
    scope='Attributed sampled porcupine damage/protection on all real Options '
          'difficulties, both port attack-timing sources and original MD. '
          'Production AOT/LLE and actual Windows visibility. Does not equate '
          'source timelines or prove complete trajectories/fractions/fatal outcomes. '
          'Historical public/contact reports are immediate bindings, not a new '
          'recursive full release-gate run.',
    source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
), indent=2) + '\n')
print('PASS' if all(checks.values()) else 'FAIL', sum(checks.values()), '/',
      len(checks), [k for k, v in checks.items() if not v], flush=True)
