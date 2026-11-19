"""Bind original Game Over evidence, retained failures and hybrid player13."""
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT / 'build/pride-game-over-bindings'
    out.mkdir()
    checks = {}
    names = [
        'pride-game-over-exits-original/report.json',
        'pride-game-over-held-original/report.json',
        'pride-game-over-exits-baseline/report.json',
        'pride-game-over-exits-player12/report.json',
        'pride-final-game-over12/build-report.json',
        'pride-game-over13/build-report.json',
        'pride-game-over13/verification/report.json',
        'pride-game-over13/verification2/report.json',
        'pride-game-over13/lifecycle/report.json',
        'pride-game-over13/lifecycle2/report.json',
        'pride-game-over13/continue-regressions/report.json',
        'pride-final-native-player11/build-report.json',
        'pride-final-native-player11/verification2/report.json',
        'pride-final-native-bindings/report.json',
    ]
    for name in names:
        bound(ROOT / 'build' / name)
        checks[name + '_bound'] = True
    player = ROOT / 'build/pride-game-over13'
    build = json.loads((player / 'build-report.json').read_text())
    checks['player13_binary'] = digest(player / 'player.exe') == build['binary_sha256'] == '137fc20cf80df72e5f11d0dd0f3dd850ced1c96e8a079081550d793c72b00b55'
    checks['all315_link_inputs'] = len(build['link_inputs_sha256']) == 315 and all(
        digest(ROOT / p) == sha for p, sha in build['link_inputs_sha256'].items())
    checks['policy_header_bound'] = 'engine/runner/tlk_continue_menu.h' in build['source_sha256']
    for folder, count in [('verification2', 160), ('lifecycle2', 34), ('continue-regressions', 171)]:
        report = json.loads((player / folder / 'report.json').read_text())
        checks[folder + '_passes'] = report['result'] == 'PASS' and len(report['checks']) == count and all(report['checks'].values())
    for folder in ['verification', 'lifecycle']:
        checks[folder + '_failure_retained'] = json.loads((player / folder / 'report.json').read_text())['result'] == 'FAIL'
    unchanged = {
        'public_player': ('build/pride-cold-boot2/player.exe', 'dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'),
        'public_launcher': ('Play Standalone Preview.cmd', 'c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'),
        'published_helper': ('dist/PrepareFinalAssets.exe', '4dfa39a2d902f820dab445470ea97d7e611b2187d62afefb569c51bb9658072b'),
        'native_package': ('build/pride-final-native-installed/native.assets', '62cd92f329d44baf6f476b633952b6e23046959b1b6c364e7600a9398515311e'),
    }
    for label, (path, sha) in unchanged.items():
        checks[label + '_unchanged'] = digest(ROOT / path) == sha
    manifest = ROOT / 'build/pride-final-native-installed/actual install/install.json'
    info = json.loads(manifest.read_text())
    checks['installed_md_menu_unchanged'] = digest(manifest.parent / info['menu_assets']['file']) == 'f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    checks['framework_submodules_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT / 'engine', text=True).strip()
    paths = [Path(__file__), manifest, *[ROOT / 'build' / name for name in names]]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], sum(checks.values()), '/', len(checks), flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
