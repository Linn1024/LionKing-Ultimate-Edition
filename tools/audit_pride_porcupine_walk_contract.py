"""Bind full original walking continuation and ordinary MD cue eligibility."""
import csv
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-porcupine-walk-contract'
    out.mkdir()
    paths = [Path(__file__)]
    def read(relative):
        path = ROOT/relative
        paths.append(path)
        return bound(path)
    fixtures = read('build/pride-porcupine-walk-originals/report.json')
    original = read('build/md-porcupine-idle-roar2/report.json')
    component = read('build/pride-porcupine-component/report.json')
    checks = dict(full_original_continuations49=fixtures['result'] == 'PASS'
                  and len(fixtures['checks']) == 49 and all(fixtures['checks'].values()),
                  no_original_callee_intercepts=fixtures['intercepted_callees'] == [],
                  twenty_four_snapshot_fixtures=len(fixtures['cases']) == 24)
    ordinary = []
    for name in ('3280-32', '3280-80', '3300-56', '3300-80'):
        installed = original['cases'][name]['installed'][0]
        actor = installed['actor']
        field = int(installed['field'])
        path = ROOT/'build/md-porcupine-idle-roar2'/name/'calls.csv'
        paths.append(path)
        rows = [r for r in csv.DictReader(path.open()) if r['actor'] == actor
                and field <= int(r['field']) <= field+29]
        attacks = [r for r in rows if r['pc'] == '19a446']
        cues = [r for r in rows if r['pc'] == '19a594']
        checks[name+'_countdown'] = [(int(r['field']), int(r['timer'])) for r in attacks] == [
            (field+1+i, 27-i) for i in range(28)]
        checks[name+'_no_timer28_cue'] = not cues
        ordinary.append(dict(case=name, actor=actor, facing=installed['facing'],
                             installation_field=field, attack_entries=len(attacks), cue_calls=len(cues)))
    checks['natural_countdowns_both_facings'] = {r['facing'] for r in ordinary} == {'0', '1'}
    adapted = [r for r in component['cases'] if r['inputs'][:4] == [1, 27, 0, 1]]
    checks['existing_adapter_eight_timer27_cases'] = (component['result'] == 'PASS'
        and len(adapted) == 8 and all(r['observed'][:18] == r['original_md'] for r in adapted)
        and all(r['observed'][0] == 26 and r['observed'][15] == 0 for r in adapted))
    search = read('build/pride-porcupine-walk-roar7/report.json')
    checks['held_jump_negative_search_retained'] = search['result'] == 'NO_LATE_ENTRY_FOUND'
    for name in search['cases']:
        capture = read(f'build/pride-porcupine-roar-observer/{name}/report.json')
        checks[name+'_exited'] = capture['returncode'] == 0
    build = read('build/pride-porcupine38/build-report.json')
    checks['production_unchanged_321_inputs'] = (digest(ROOT/'build/pride-porcupine38/player.exe') == build['binary_sha256']
        and len(build['link_inputs_sha256']) == 321
        and all(digest(ROOT/p) == sha for p, sha in build['link_inputs_sha256'].items()))
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT/'engine').strip()
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  original_md_ordinary_countdowns=ordinary,
                  existing_adapter_component_external_services_intercepted=True,
                  ordinary_port_walking_response_proven=False, new_runtime_change_required=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks),
          [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
