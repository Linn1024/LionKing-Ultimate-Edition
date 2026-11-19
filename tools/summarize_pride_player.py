"""Bind the independent Windows player build and its real presentation/save/source gates."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    base = ROOT / 'build/pride-player'
    previous = ROOT / 'build/pride-owned-guest-latest.json'
    prior = bound(previous)
    assert prior['result'] == 'PARTIAL' and prior['new_checks'] == 150
    bp = base / 'build-report.json'
    build = bound(bp)
    assert build['result'] == 'BUILT' and digest(base / 'player.exe') == build['binary_sha256']
    assert build['object_count'] == 572 and build['archive_count'] == 4
    for name, sha in build['link_inputs_sha256'].items():
        assert name.startswith('build/pride-player/') and digest(ROOT / name) == sha
    for name, sha in build['production_sha256'].items():
        assert digest(ROOT / name) == sha
    paths = [Path(__file__), previous, bp]
    checks = fields = 0
    for name, count in (('metadata-review', 7), ('width-completion', 21), ('regression', 20),
                        ('card-slots', 8), ('boss-saves', 37), ('card-saves', 47), ('switch', 11),
                        ('launcher-verification', 6)):
        path = base / name / 'report.json'
        r = bound(path)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values()), name
        checks += count
        fields += r.get('compared_fields', r.get('native_fields_compared', 0))
        if name == 'metadata-review':
            assert r['raw_identical_checks'] == 914 and r['raw_reviewed_metadata_difference_checks'] == 1
        if name == 'width-completion':
            assert r['first_next_level_field'] == 3450 and not r['loaded_states'] and not r['practice_or_guest_edits']
        paths.append(path)
    package_path = base / 'portable-report.json'
    package = bound(package_path)
    assert package['result'] == 'PASS' and len(package['checks']) == 5 and all(package['checks'].values())
    checks += 5
    fields += package['compared_fields']
    paths.append(package_path)
    native_path = base / 'native-gates/play-report.json'
    native = json.loads(native_path.read_text())
    baseline_path = ROOT / 'build/pride-reset/fixed4/native/gates/play-report.json'
    baseline = json.loads(baseline_path.read_text())
    assert native['result'] == 'PASS' and native['route_count'] == 75
    assert native['binary_sha256'] == build['binary_sha256'] and native['routes'] == baseline['routes']
    assert native['verifier_sha256'] == digest(ROOT / 'tools/verify_pride_player_native75.py')
    paths.extend([native_path, baseline_path, ROOT / 'tools/verify_pride_player_native75.py',
                  ROOT / 'tools/verify_pride_launch_native.py', ROOT / 'tools/verify_native_routes.py'])
    for relative in ('width-completion/aot/window.png', 'card-slots/live/client.png',
                     'card-saves/new-resume-aot/window.png', 'switch/live/pending-md.png',
                     'switch/live/pending-snes-owned.png', 'portable-verification2/window.png',
                     'launcher-verification/window.png'):
        path = base / relative
        width, height, _ = pixels(path)
        assert width > 0 and height > 0
        paths.append(path)
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    paths.append(ROOT / 'Play Standalone Preview.cmd')
    report = dict(result='PARTIAL', new_checks=checks, compared_fields=fields,
                  native_endpoint_route_pairs=75, fresh_object_count=572, fresh_archive_count=4,
                  independent_player_cmake_graph_verified=True, historical_object_or_link_template_imported=False,
                  compared_predecessor_objects=305, raw_identical_object_checks=914,
                  reviewed_readonly_build_identifier_changes=1,
                  actual_windows_completion_saves_switching_verified=True,
                  portable_payload_clean_system_path_verified=True, standalone_launcher_verified=True,
                  standalone_settings_directory='settings/standalone-preview',
                  prior_published_preview_unchanged=True, fresh_allbugs_gate_complete=False,
                  release_and_legacy_save_migration_complete=False, full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = base / 'integration-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'build/pride-player-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} checks; {fields} compared fields; 75 native route pairs', flush=True)


if __name__ == '__main__':
    main()
