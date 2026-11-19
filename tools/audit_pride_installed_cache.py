"""Bind installation behavior, complete route, regression gates and retained failures."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-installed-cache41'
    out = base/'bindings'
    out.mkdir()
    paths = [Path(__file__)]
    checks = {}
    for folder, count in [('verification', 80), ('setup-verification', 26), ('transparency', 9),
                          ('scope-verification', 3), ('native75', 302), ('allbugs-verification', 13)]:
        path = base/folder/'report.json'
        data = bound(path)
        paths.append(path)
        checks[folder] = data['result'] == 'PASS' and len(data['checks']) == count and all(data['checks'].values())
    for label, path in [('anchor_attempt', ROOT/'build/pride-installed-cache39/report.json'),
                         ('empty_path_attempt', ROOT/'build/pride-installed-cache40/empty-path/report.json')]:
        data = bound(path)
        paths.append(path)
        checks[label+'_failure_retained'] = data['result'] in ('FAIL', 'FAILED_PATCH_ANCHOR')
    build_path = base/'build-report.json'
    build = bound(build_path)
    paths.append(build_path)
    checks['candidate_and_all321_inputs_bound'] = (digest(base/'player.exe') == build['binary_sha256']
        and len(build['link_inputs_sha256']) == 321
        and all(digest(ROOT/p) == sha for p, sha in build['link_inputs_sha256'].items()))
    checks['only_two_link_inputs_changed'] = build['unchanged_link_inputs'] == 319
    observer_path = base/'allbugs-observer/build-report.json'
    observer = bound(observer_path)
    paths.append(observer_path)
    checks['observer_only_host_differs'] = observer['nonhost_inputs_unchanged'] == 320 and len(observer['link_inputs_sha256']) == 321
    checks['public_launcher_unchanged'] = digest(ROOT/'Play Standalone Preview.cmd') == 'c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['public_preview_unchanged'] = digest(ROOT/'build/pride-cold-boot2/player.exe') == 'dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['preparation_helper_unchanged'] = digest(ROOT/'dist/PrepareFinalAssets.exe') == '1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT/'engine').strip()
    paths += [ROOT/'engine/cmake/game-patches/zz-installed-scene-cache.hunks',
              ROOT/'engine/cmake/game-patches/zzz-installed-scene-cache-scope.hunks',
              ROOT/'engine/cmake/final-frontend-patches/zz-installed-scene-cache.hunks']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  whole_installation_only_migration_complete=False, full_first_level_fidelity_complete=False,
                  public_package_changed=False, fresh_standalone_build_graph_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
