"""Bind prepared widgets and GPU-clock research without claiming full scene fidelity."""
import hashlib
import json
from pathlib import Path

from audit_scenes import ROOT
import summarize_pride_hud_binding


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(report):
    for name, sha in report['source_sha256'].items():
        assert digest(ROOT / name) == sha, name


def main():
    summarize_pride_hud_binding.main()
    references = {}

    def load(name, relative, result='PASS'):
        path = ROOT / relative
        report = json.loads(path.read_text())
        assert report['result'] == result, (name, report['result'])
        references[name] = dict(path=relative, sha256=digest(path))
        return path, report

    _, parent = load('retained_production', 'build/pride-hud-binding-latest.json', 'PARTIAL')
    _, gpu = load('original_gpu_clock', 'build/pride-gpu-clock/report.json')
    sources(gpu)
    assert (gpu['death_fields'], gpu['revival_fields'], gpu['compared_texture_indices']) == (248, 74, 507776)
    assert gpu['preceding_gameplay_retained_at_death0'] and gpu['static_checkpoint_head_separate']
    path, sat = load('original_md_sat', 'build/pride-scene-sat-full/report.json')
    sources(sat)
    assert sat['fields'] == 361 and sat['prefix_full_ram_checks'] == 40
    assert not sat['guest_edits'] and not sat['loaded_states']
    for name, sha in sat['artifacts_sha256'].items():
        assert digest(path.parent / name) == sha, name
    path, hud = load('native_widget_oracle', 'build/pride-native-hud-oracle/report.json')
    sources(hud)
    assert hud['probe_sha256'] == digest(ROOT / 'engine/build-win/tlk_native_hud_oracle.exe')
    assert (hud['health_cases'], hud['roar_cases'], hud['original_cpu_font_bytes']) == (9, 57, 33792)
    assert hud['oracle_guest_value_fixtures'] and not hud['ordinary_gameplay_proof']
    assert hud['ordinary_checkpoint_widget_targets_exact'] and hud['source_detached'] and hud['alias_safe']
    assert hud['atomic_rejection_and_full_rom_identity_verified']
    for name, sha in hud['artifacts_sha256'].items():
        assert digest(path.parent / name) == sha, name
    path, oam = load('native_oam', 'build/pride-scene-oam-audit/report.json', 'AUDITED')
    assert oam['fields'] == 121 and oam['read_only_guest_and_full_tracked_ram_exact']
    for key, relative in dict(script='tools/analyze_pride_scene_oam.py', probe='tools/pride_scene_oam_audit.c',
                              binary='engine/build-win/tlk_scene_oam_probe.exe').items():
        assert digest(ROOT / relative) == oam['source_sha256'][key], relative
    for key, relative in dict(raw='native/native-oam.bin', analysis='native/analysis.json').items():
        assert digest(path.parent / relative) == oam['artifacts_sha256'][key], relative
    analysis = {row['age']: row for row in json.loads((path.parent / 'native/analysis.json').read_text())}
    assert analysis[268]['recorded'] == 25 and not analysis[268]['matching_recorded_slots']
    assert not analysis[273]['recoverable268_slots'] and analysis[273]['recorded'] == 0
    assert len(analysis[298]['matching_recorded_slots']) == 25
    _, widgets = load('presented_native_widgets', 'build/pride-prepared-widget-pixels/report.json')
    sources(widgets)
    assert len(widgets['cases']) == 12 and widgets['native_health6_and_roar24_only']
    assert not widgets['original_md_widget_parity_verified']
    path, checkpoint = load('checkpoint_identity', 'build/pride-checkpoint-art/report.json')
    sources(checkpoint)
    assert checkpoint['original_native_fields'] == 63 and checkpoint['original_native_oam_texture_indices'] == 68544
    assert checkpoint['copied_ram_cases'] == 334 and checkpoint['relocated_task_and_draw_fixtures'] == 2
    assert checkpoint['duplicate_producer_fields'] == [346] and not checkpoint['classification_proves_visibility']
    for name, sha in checkpoint['artifacts_sha256'].items():
        assert digest(path.parent / name) == sha, name
    path, checkpoint_art = load('checkpoint_art', 'build/pride-checkpoint-art/art-report.json')
    sources(checkpoint_art)
    assert checkpoint_art['independent_frame_palette_combinations'] == 4 and checkpoint_art['source_indexed_pixels'] == 2046
    assert checkpoint_art['sampled_colors'] == 4092 and checkpoint_art['source_detached']
    assert checkpoint_art['original_native_full_palette_fields'] == 63
    assert checkpoint_art['original_md_static_head_palette_bank_fields'] == 74
    assert not checkpoint_art['renderer_integration'] and not checkpoint_art['actual_windows_captured']
    for name, sha in checkpoint_art['artifacts_sha256'].items():
        assert digest(path.parent / name) == sha, name
    assert 'tlk_checkpoint_art' not in (ROOT / 'engine/CMakeLists.txt').read_text()
    assert 'tlk_checkpoint_role' not in (ROOT / 'engine/runner/tlk_wide.c').read_text()

    cases = owned = compared = window_pixels = 0
    release_ages = {}
    for host in ('headless', 'sdl'):
        for width in (256, 320):
            path, report = load(f'{host}-{width}',
                f'build/pride-scene-render-prepared-{host}-{width}-5400/report.json',
                'OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN')
            sources(report)
            assert report['prepared_objects'] and report['capture_action'] == 'fresh_replay'
            assert len(report['runs']) == 8
            binary = ROOT / f'engine/build-win/tlk_scene_prepared_{"sdl" if host == "sdl" else "probe"}.exe'
            assert report['probe_sha256'] == digest(binary)
            for case, result in report['runs'].items():
                folder = path.parent / case
                capture = json.loads((folder / 'capture.json').read_text())
                assert capture['execution_completed'] and capture['probe_sha256'] == report['probe_sha256']
                sources(capture)
                assert capture['profile_sha256'] == digest(folder / 'resources.ini')
                for name, sha in result['artifacts_sha256'].items():
                    assert digest(folder / name) == sha, (host, width, case, name)
                if case.endswith('-owned'):
                    assert result['owned_fields'] == result['release_age'] + 1
                    assert 345 <= result['release_age'] <= 353 and result['black_reload_and_restore_verified']
                    owned += 1
                    compared += result['pixels_compared']
                    release_ages[f'{host}-{width}-{case}'] = result['release_age']
                cases += 1
    assert (cases, owned) == (32, 16)
    for width in (256, 320):
        path, report = load(f'active_windows-{width}', f'build/pride-scene-prepared-windows-{width}/report.json')
        sources(report)
        assert report['prepared_objects'] and report['width'] == width and len(report['runs']) == 4
        assert report['probe_sha256'] == digest(ROOT / 'engine/build-win/tlk_scene_prepared_sdl.exe')
        for case, result in report['runs'].items():
            assert result['actual_window_matches_owned_pixels'] and result['identical_duplicate_presentations'] == 1
            window_pixels += result['exact_window_pixels']
            for name, sha in result['artifacts_sha256'].items():
                assert digest(path.parent / case / name) == sha, (width, case, name)
    default = next(line for line in (ROOT / 'engine/build-win/build.ninja').read_text().splitlines()
                   if line.startswith('build all:'))
    assert all(target not in default for target in ('tlk_scene_prepared_', 'tlk_scene_oam_probe', 'tlk_native_hud_oracle'))
    result = dict(result='PARTIAL', scope=__doc__, production_sha256=parent['production_sha256'],
        scene_pixel_cases=cases, owned_cases=owned, independently_compared_pixels=compared,
        actual_active_windows=8, actual_window_pixels_compared=window_pixels,
        canonical_cpu_ready_age=345, native_pixel_exact_handoff_ages=release_ages,
        original_gpu_texture_indices=507776, original_native_widget_bytes=33792,
        independently_compared_native_widget_pixels=widgets['independently_compared_opaque_widget_pixels'],
        checkpoint_semantic_identity_and_owned_art_verified=True, checkpoint_renderer_integrated=False,
        production_behavior_enabled=False, full_first_level_fidelity_complete=False,
        complete_hud_npc_revival_ownership=False, compiled_scene_ownership=False,
        evidence=references, source_sha256={'tools/summarize_pride_prepared_objects.py': digest(Path(__file__))},
        remaining=[
            'Integrate checkpoint-head component with independent choices and physical OAM ownership; adapt remaining auxiliary objects',
            'Verify original MD widget restoration semantics and source-specific placement/priority/layout',
            'Implement player scene lifetime, active saves, pause/reset/source switching and compiled ownership',
            'Verify boundary input, default/final-life paths and native audio policy/phase',
            'Complete and audit the full Pride Lands checklist before creating the remaining-levels goal'
        ] + parent['remaining'])
    (ROOT / 'build/pride-prepared-objects-latest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'{cases} scene cases, {compared} pixels, eight exact active Windows captures; full Pride remains PARTIAL', flush=True)


if __name__ == '__main__':
    main()
