"""Bind maintained guest generation, all replacement objects and actual Windows gates."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    base = ROOT / 'build/pride-owned-guest2'
    generation = ROOT / 'build/pride-owned-guest-generation'
    previous = ROOT / 'build/pride-owned-core-latest.json'
    prior = bound(previous)
    assert prior['result'] == 'PARTIAL' and prior['new_checks'] == 155
    bp = base / 'build-report.json'
    build = bound(bp)
    assert build['result'] == 'BUILT' and digest(base / 'player.exe') == build['binary_sha256']
    assert len(build['replacements']) == 28 and build['remaining_historical_staged_replacement_objects'] == 0
    for name, sha in build['link_inputs_sha256'].items():
        assert digest(ROOT / name) == sha, name
        assert not name.startswith('build/') or name.startswith('build/pride-owned-guest2/'), name
    for name, sha in build['production_sha256'].items():
        assert digest(ROOT / name) == sha, name
    gp = generation / 'generation-report.json'
    generated = bound(gp)
    assert generated['result'] == 'GENERATED' and len(generated['generated_sha256']) == 14
    for name, sha in generated['generated_sha256'].items():
        assert digest(generation / name) == sha, name
    assert (base / 'save-compatibility.json').read_bytes() == (ROOT / 'build/pride-owned-core/save-compatibility.json').read_bytes()
    paths = [Path(__file__), previous, bp, gp, base / 'build.log']
    checks = fields = 0
    for folder, name, count in ((generation, 'verification', 17), (base, 'code-equivalence', 84),
                                (base, 'width-completion', 21), (base, 'regression', 20), (base, 'card-slots', 8)):
        path = folder / name / 'report.json'
        r = bound(path)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values()), name
        checks += count
        fields += r.get('compared_fields', r.get('native_fields_compared', 0))
        if name == 'code-equivalence':
            assert len(r['objects']) == 28
        if name == 'verification':
            assert r['native_units_compared'] == r['rng_units_compared'] == 137 and r['hook_units_compared'] == 13
        if name == 'width-completion':
            assert r['first_next_level_field'] == 3450 and not r['loaded_states'] and not r['practice_or_guest_edits']
        paths.append(path)
    for name in ('width-completion/aot/window.png', 'card-slots/live/client.png'):
        path = base / name
        assert pixels(path)[:2] == (512, 448)
        paths.append(path)
    paths += [ROOT / 'engine/cmake/TlkPrideGuest.cmake', ROOT / 'engine/scripts/validate_pride_generation.py']
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    report = dict(result='PARTIAL', new_checks=checks, compared_fields=fields, preceding_owned_core_checks=155,
                  freshly_built_replacement_objects=28, historical_staged_replacement_objects=0,
                  native_hook_disabled_units_exact=137, rng_generation_units_exact=137,
                  all_replacement_section_bytes_sizes_and_relocations_preserved=True,
                  final_standalone_player_cmake_link_integrated=False,
                  ordinary_engine_objects_and_link_template_still_reused=True,
                  save_contract_unchanged=True, public_preview_unchanged=True,
                  source_or_rendered_scene_capability_changed=False, full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = base / 'integration-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'build/pride-owned-guest-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} checks; {fields} fields; no historical staged replacement objects', flush=True)


if __name__ == '__main__':
    main()
