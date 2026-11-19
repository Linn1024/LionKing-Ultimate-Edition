"""Bind fresh maintained runtime/helper builds and their Windows replay gates."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    base = ROOT / 'build/pride-owned-core'
    previous = ROOT / 'build/pride-owned-host-latest.json'
    prior = bound(previous)
    assert prior['result'] == 'PARTIAL' and prior['new_checks'] == 129
    bp = base / 'build-report.json'
    build = bound(bp)
    assert build['result'] == 'BUILT' and digest(base / 'player.exe') == build['binary_sha256']
    for name, sha in build['link_inputs_sha256'].items():
        assert digest(ROOT / name) == sha, name
    for name, sha in build['production_sha256'].items():
        assert digest(ROOT / name) == sha, name
    assert len(build['replacements']) == 14 and build['remaining_staged_nonhost_objects'] == 14
    assert len(build['remaining_staged_inputs_sha256']) == 14
    assert all('bankc' in name or name.endswith('/clear.obj') for name in build['remaining_staged_inputs_sha256'])
    assert (base / 'save-compatibility.json').read_bytes() == (ROOT / 'build/pride-owned-host3/save-compatibility.json').read_bytes()
    paths = [Path(__file__), previous, bp]
    guest_evidence = base / 'guest-rebuild-evidence.json'
    evidence = bound(guest_evidence)
    assert evidence['result'] == 'INCOMPLETE' and len(evidence['instrumented_units']) == 13
    assert evidence['remaining_guest_objects'] == build['remaining_staged_inputs_sha256']
    paths.extend([guest_evidence, base / 'build.log'])
    checks = fields = 0
    for name, count in (('code-equivalence', 42), ('width-completion', 21), ('boss-saves', 37),
                        ('card-saves', 47), ('card-slots', 8)):
        path = base / name / 'report.json'
        r = bound(path)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values()), name
        checks += count
        fields += r.get('compared_fields', r.get('native_fields_compared', 0))
        if name == 'code-equivalence':
            assert len(r['objects']) == 14 and r['ignored_compiler_metadata_section'] == '.rdata$zzz'
        if name == 'width-completion':
            assert r['first_next_level_field'] == 3450 and not r['loaded_states'] and not r['practice_or_guest_edits']
        paths.append(path)
    for name in ('width-completion/aot/window.png', 'boss-saves/new-aot/window.png',
                 'card-saves/new-resume-aot/window.png', 'card-slots/live/client.png'):
        path = base / name
        assert pixels(path)[:2] == (512, 448)
        paths.append(path)
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    report = dict(result='PARTIAL', new_checks=checks, compared_fields=fields, preceding_owned_host_checks=129,
                  fresh_cmake_host_and_runtime_helper_objects=14,
                  all_runtime_section_bytes_sizes_and_relocations_preserved=True,
                  remaining_staged_guest_objects=14, all_non_guest_staged_objects_replaced=True,
                  entire_player_built_without_historical_staged_objects=False,
                  source_asset_renderer_capabilities_changed=False, save_contract_unchanged=True,
                  public_preview_unchanged=True, full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = base / 'integration-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'build/pride-owned-core-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} checks; {fields} fields; 14 guest objects remain', flush=True)


if __name__ == '__main__':
    main()
