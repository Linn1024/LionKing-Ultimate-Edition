"""Collect clean-source/CMake host migration and actual Windows behavior evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    base = ROOT / 'build/pride-owned-host3'
    previous = ROOT / 'build/pride-owned-save-context-latest.json'
    p = bound(previous)
    assert p['result'] == 'PARTIAL' and p['new_checks'] == 84
    paths = [Path(__file__), previous]
    builds = []
    for folder in (ROOT / 'build/pride-rng-player7', base):
        path = folder / 'build-report.json'
        r = bound(path)
        assert r['result'] == 'BUILT' and digest(folder / 'player.exe') == r['binary_sha256']
        for name, sha in r['link_inputs_sha256'].items():
            assert digest(ROOT / name) == sha, name
        for name, sha in r['production_sha256'].items():
            assert digest(ROOT / name) == sha, name
        paths.append(path)
        builds.append(r)
    assert builds[1]['host_compiled_from_owned_sources'] and not builds[1]['historical_host_include_dependencies']
    core = lambda r: {k: v for k, v in r['link_inputs_sha256'].items() if not k.endswith('/host.obj')}
    assert core(builds[0]) == core(builds[1])
    assert (base / 'save-compatibility.json').read_bytes() == (ROOT / 'build/pride-rng-player7/save-compatibility.json').read_bytes()
    checks = fields = 0
    reports = {}
    for name, count in (('code-equivalence', 7), ('cmake-host', 6), ('width-completion', 21),
                        ('boss-saves', 37), ('card-saves', 47), ('switch', 11)):
        path = base / name / 'report.json'
        r = bound(path)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values()), name
        checks += count
        fields += r.get('compared_fields', r.get('native_fields_compared', 0))
        paths.append(path)
        reports[name] = r
    assert reports['code-equivalence']['compared_host_tail_tokens'] == 386078
    assert reports['width-completion']['first_next_level_field'] == 3450
    assert not reports['width-completion']['loaded_states'] and not reports['width-completion']['practice_or_guest_edits']
    assert not reports['cmake-host']['historical_host_object_linked']
    remaining = base / 'remaining-staged-inputs.json'
    todo = json.loads(remaining.read_text())
    assert todo['result'] == 'INCOMPLETE' and todo['count'] == 27
    for name, sha in todo['remaining_nonhost_staged_link_inputs_sha256'].items():
        assert builds[1]['link_inputs_sha256'][name] == digest(ROOT / name) == sha
    paths.append(remaining)
    for relative in ('width-completion/aot/window.png', 'boss-saves/new-aot/window.png',
                     'card-saves/new-resume-aot/window.png', 'switch/live/pending-md.png',
                     'switch/live/pending-snes-owned.png'):
        path = base / relative
        assert pixels(path)[:2] == (512, 448)
        paths.append(path)
    paths += [ROOT / 'engine/cmake/TlkPrideHost.cmake', ROOT / 'engine/runner/pride/README.md']
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    report = dict(result='PARTIAL', new_checks=checks, compared_fields=fields,
                  preceding_owned_eligibility_checks=84, host_machine_code_data_relocations_identical=True,
                  independent_cmake_host_object_verified=True, actual_windows_completion_saves_switching_verified=True,
                  preceding_nonhost_objects_unchanged=True, tested_save_contract_unchanged=True,
                  whole_binary_independent_of_historical_objects=False,
                  remaining_staged_nonhost_objects=27,
                  busy_cache_serialization_implemented=False, public_preview_unchanged=True,
                  full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = base / 'integration-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'build/pride-owned-host-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} checks; {fields} fields; owned host/CMake verified', flush=True)


if __name__ == '__main__':
    main()
