"""Bind retained ordinary walking-response searches without promoting idle cases."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT / 'build/pride-porcupine-walk-search-audit'
    out.mkdir()
    paths = [Path(__file__)]
    cases = []
    checks = {}
    for suffix in ('', '2', '3', '4', '5', '6'):
        source = ROOT / f'build/pride-porcupine-walk-roar{suffix}/report.json'
        report = bound(source)
        paths.append(source)
        for label, case in report['cases'].items():
            capture = ROOT / 'build/pride-porcupine-roar-observer' / label / 'report.json'
            actual = bound(capture)
            paths.append(capture)
            checks[label + '_exited'] = actual['returncode'] == 0
            entries = case['first_attack_by_actor']
            target = entries.get('b913') if suffix != '2' else None
            cases.append(dict(case=label, target_entry=target,
                              generic_capture_result=actual['result'],
                              idle_shaped_late_entry=bool(target and target['timer'] == '28'),
                              walking_response_proven=False))
    debug_path = ROOT / 'build/pride-porcupine-walk-calls-search/report.json'
    debug = bound(debug_path)
    paths.append(debug_path)
    checks['neutral_debugger_evidence_retained'] = (
        debug['result'] == 'FAIL'
        and not debug['checks']['walking_helper_called']
        and not debug['checks']['actual_original_caller_chain']
        and sum(debug['checks'].values()) == 7)
    build_path = ROOT / 'build/pride-porcupine38/build-report.json'
    build = bound(build_path)
    paths.append(build_path)
    checks['production_unchanged'] = digest(build_path.parent / 'player.exe') == build['binary_sha256']
    checks['all_321_inputs_unchanged'] = len(build['link_inputs_sha256']) == 321 and all(
        digest(ROOT / p) == sha for p, sha in build['link_inputs_sha256'].items())
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT / 'engine').strip()
    checks['23_ordinary_branches_retained'] = len(cases) == 23
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  cases=cases, walking_response_proven=False, runtime_changed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], sum(checks.values()), '/', len(checks),
          'idle-shaped entries', sum(c['idle_shaped_late_entry'] for c in cases),
          'walking response remains unverified', flush=True)


if __name__ == '__main__':
    main()
