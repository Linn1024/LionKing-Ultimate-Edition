"""Bind the native reset repair without claiming mixed-player lifecycle coverage."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-reset'
    paths = [Path(__file__)]
    checks = {}
    reports = {}

    def report(path, result='PASS'):
        value = bound(path)
        assert value['result'] == result, (path, value['result'])
        if result == 'PASS':
            assert all(value.get('checks', {}).values()), path
        paths.append(path)
        reports[str(path.relative_to(ROOT)).replace('\\', '/')] = digest(path)
        return value

    builds = {}
    for folder in ('fixed2', 'views2', 'audio-views', 'audio-views2'):
        build = report(base / folder / 'build-report.json', 'BUILT')
        builds[folder] = build
        for name, sha in build['production_sha256'].items():
            assert digest(ROOT / name) == sha, name
        for host, run in build['runs'].items():
            binary = base / folder / (('native-' + host if folder == 'fixed2' else host + '-reset') + '.exe')
            assert digest(binary) == run['binary_sha256'], binary
            for name, sha in run['link_inputs_sha256'].items():
                assert digest(ROOT / name) == sha, name
    before = report(base / 'before/boundaries/report.json', 'REPRODUCED')
    boundary = report(base / 'fixed2/boundaries/report.json')
    for host in ('headless', 'sdl'):
        failed = report(base / 'views/matrix' / host / 'report.json', 'INCOMPLETE')
        checks['before/' + host + '/warm_replay_failure_reproduced'] = not failed['checks']['soft-aot-1211/complete_pcm']
    report(base / 'audio-views/invalid-setup-report.json', 'INVALID_TEST_SETUP')
    checks['before/failure_reproduced'] = not before['checks']['all_fresh_boundaries']
    checks.update({'boundary/' + k: v for k, v in boundary['checks'].items()})
    for folder, expected in (('fixed', 1), ('fixed2', 0)):
        shadow = report(base / folder / 'shadow/report.json', 'OBSERVED')
        for kind in ('soft', 'init'):
            rows = [r for r in shadow['observations'][kind] if r['kind'] == kind]
            a, b = rows[-2:]
            checks[folder + '/' + kind + '/fastrom'] = a['memsel'] == 1 and b['memsel'] == expected
            checks[folder + '/' + kind + '/hdma'] = b['hdma'] == 0
    for host in ('headless', 'sdl'):
        r = report(base / 'views2/matrix' / host / 'report.json')
        assert r['binary_sha256'] == builds['views2']['runs'][host]['binary_sha256']
        checks.update({host + '/' + k: v for k, v in r['checks'].items()})
    audio = report(base / 'audio-views2/matrix/sdl/report.json')
    assert audio['binary_sha256'] == builds['audio-views2']['runs']['sdl']['binary_sha256']
    assert audio['selected_md_audio_reset_verified']
    checks.update({'md-audio/' + k: v for k, v in audio['checks'].items()})
    for relative, host in (('early-state/report.json', 'headless'), ('windows/report.json', 'sdl')):
        r = report(base / 'fixed2' / relative)
        identity = r['binary_sha256'] if host == 'headless' else r['after_binary_sha256']
        assert identity == builds['fixed2']['runs'][host]['binary_sha256']
        checks.update({relative + '/' + k: v for k, v in r['checks'].items()})
    for filename in ('play-report.json', 'allbugs-report.json'):
        path = base / 'fixed2/native/gates' / filename
        r = report(path)
        assert r['binary_sha256'] == builds['fixed2']['runs']['headless']['binary_sha256']
        assert r['verifier_sha256'] == digest(ROOT / 'tools/verify_native_routes.py')
        prior_path = ROOT / 'build/pride-raster-state/native/gates' / filename
        prior = report(prior_path)
        checks[filename + '/previous_endpoints'] = r['routes'] == prior['routes']
        if filename == 'allbugs-report.json':
            a = path.parent / 'allbugs-aot.ram'
            b = path.parent / 'allbugs-lle.ram'
            old = prior_path.parent / 'allbugs-aot.ram'
            checks['allbugs/previous_every_field_ram'] = a.read_bytes() == b.read_bytes() == old.read_bytes()
            checks['allbugs/current_every_field_ram'] = r['allbugs_tracked_ram_equal_every_frame']
            paths.extend((a, b, old))
    assert all(checks.values()), [k for k, v in checks.items() if not v]
    result = dict(result='PARTIAL', scope=__doc__, checks=checks, checks_passed=len(checks),
                  reports_sha256=reports,
                  source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in paths},
                  native_reset_boundaries=12, native_reset_replay_cases=16,
                  native_reset_compared_fields=48000, native_reset_pcm_exact=True,
                  selected_md_audio_reset_verified=True, selected_md_audio_reset_replay_cases=8,
                  selected_md_audio_compared_fields=24000, private_revival_reset_verified=False,
                  profile_noop_apply_after_reset_verified=False,
                  public_player_enabled=False, full_first_level_fidelity_complete=False)
    (ROOT / 'build/pride-reset-latest.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PARTIAL native reset:', len(checks), 'checks; 16 replay cases; 48000 fields', flush=True)


if __name__ == '__main__':
    main()
