"""Aggregate second-level background evidence without enabling its adapter.

Keep historical cached disagreement counters separate from the fresh execution
and VDP timing proof. Native offset/palette correspondence remains unfinished.
"""
import collections
import hashlib
import json
from audit_scenes import ROOT


def main():
    source = ROOT/'build/md-next-levels-replay/scene-backgrounds.json'
    rows = [r for r in json.loads(source.read_text()) if r['level'] == 1]
    visible = [r for r in rows if r['display_enabled'] and r['normal_background_palette_variants']]
    assert len(visible) > 7000
    mismatches = [r for r in visible if r['scroll_previous_errors'] != 0]
    timing_path = ROOT/'build/cant-wait-timing/report.json'
    timing = json.loads(timing_path.read_text())
    assert timing['result'] == 'PASS' and not timing['previous_input_unmatched_fields']
    assert timing['visible_fields'] == len(visible) and timing['matched_vdp_fields'] == len(visible)
    assert timing['trace_sha256'] == hashlib.sha256((timing_path.parent/'callbacks.csv').read_bytes()).hexdigest()
    assert timing['source_sha256'] == hashlib.sha256((source.parent/'frames.json').read_bytes()).hexdigest()
    native_path = ROOT/'build/cant-wait-native/report.json'
    palette_path = ROOT/'build/cant-wait-palette/report.json'
    native = json.loads(native_path.read_text())
    palette = json.loads(palette_path.read_text())
    assert native['result'] == 'WRAP_INPUTS_VERIFIED_PALETTE_LIFECYCLE_OPEN'
    assert native['audit_source_sha256'] == hashlib.sha256((ROOT/'tools/audit_cant_wait_native.py').read_bytes()).hexdigest()
    assert native['headless_sha256'] == hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest()
    assert native['md_reference_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert palette['result'] == 'OBSERVED_PENDING_NATIVE_MAPPING'
    assert palette['original_palette_step_writes_matched'] == 39800
    assert palette['original_complete_100_color_passes'] == 398
    assert palette['input_reference_sha256'] == timing['source_sha256']
    for key, path in [('writers_csv_sha256', ROOT/'build/cant-wait-palette/writers.csv'),
                      ('trace_source_sha256', ROOT/'tools/md_cant_wait_trace.c'),
                      ('palette_recipe_source_sha256', ROOT/'tools/md_scene_background.py')]:
        assert palette[key] == hashlib.sha256(path.read_bytes()).hexdigest(), ('Stale palette evidence', key)
    renderer_path = ROOT/'build/cant-wait-renderer/report.json'
    renderer = json.loads(renderer_path.read_text())
    assert renderer['result'] == 'ORIGINAL_RENDERER_VERIFIED_PENDING_NATIVE_ADAPTER'
    assert renderer['headless_sha256'] == native['headless_sha256']
    assert renderer['player_sha256'] == hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest()
    for name, digest in renderer['source_sha256'].items():
        assert digest == hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), ('Stale renderer source', name)
    assert renderer['installed_cache_sha256'] == hashlib.sha256((ROOT/'game-data/scenes-v1.cache').read_bytes()).hexdigest()
    trigger_path = ROOT/'build/cant-wait-native-palette/report.json'
    trigger = json.loads(trigger_path.read_text())
    assert trigger['result'] == 'TRIGGER_VERIFIED_DISPLAY_TIMING_OPEN' and trigger['cases'] == 589824
    assert trigger['oracle_sha256'] == hashlib.sha256((ROOT/'build/cant_wait_native_palette.dll').read_bytes()).hexdigest()
    for name, digest in trigger['source_sha256'].items():
        assert digest == hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), ('Stale native trigger', name)
    display_path = ROOT/'build/cant-wait-display/report.json'
    display = json.loads(display_path.read_text())
    assert display['result'] == 'NATIVE_DISPLAY_CAPTURED_MD_MAPPING_OPEN'
    assert display['headless_sha256'] == native['headless_sha256']
    assert display['player_sha256'] == renderer['player_sha256']
    assert display['research_host_sha256'] == hashlib.sha256((ROOT/'engine/build-win/tlk_cant_wait_capture.exe').read_bytes()).hexdigest()
    for name, digest in display['source_sha256'].items():
        assert digest == hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), ('Stale native display source', name)
    assert display['production_hosts_unchanged'] and not display['mixed_background_enabled']
    assert display['runs']['aot'] == display['runs']['lle'] and display['runs']['aot']['fields'] == 8069
    for mode in ('aot', 'lle'):
        assert display['runs'][mode]['capture_sha256'] == hashlib.sha256((display_path.parent/mode/'fields.bin').read_bytes()).hexdigest()
    assert display['request_to_cgram_fields'] == 1
    assert [r['frame'] for r in display['actual_windows_palette_boundaries']] == [4910, 4911]
    for picture in display['actual_windows_palette_boundaries']:
        assert picture['colors_unique_to_expected_source'] > 5
        assert picture['window_sha256'] == hashlib.sha256((display_path.parent/('picture-'+str(picture['frame']))/'window.png').read_bytes()).hexdigest()
    report = {'result': 'TIMING_VERIFIED_PENDING_ADAPTER', 'scope': __doc__,
              'native_wrap_report_sha256': hashlib.sha256(native_path.read_bytes()).hexdigest(),
              'palette_writer_report_sha256': hashlib.sha256(palette_path.read_bytes()).hexdigest(),
              'c_renderer_report_sha256': hashlib.sha256(renderer_path.read_bytes()).hexdigest(),
              'original_c_renderer_pixels_per_initialization': renderer['original_pixels_per_initialization'],
              'original_c_fade_writes_per_initialization': renderer['original_fade_writes_per_initialization'],
              'immutable_rom_recipe_hydration_verified': True,
              'native_trigger_report_sha256': hashlib.sha256(trigger_path.read_bytes()).hexdigest(),
              'original_native_trigger_fixture_cases': trigger['cases'],
              'native_display_report_sha256': hashlib.sha256(display_path.read_bytes()).hexdigest(),
              'native_display_fields_per_execution_mode': 8069,
              'native_request_to_cgram_fields': 1,
              'actual_windows_palette_boundary_fields': [4910, 4911],
              'native_sampled_wrap_unit': native['wrap_unit_pixels'],
              'original_palette_step_writes_matched': palette['original_palette_step_writes_matched'],
              'checkpoint_only_palette_disagreements': native['md_checkpoint_only_palette_disagreements'],
              'md_descriptor_palette_is_ram': native['md_descriptor_palette_is_ram'],
              'timing_report_sha256': hashlib.sha256(timing_path.read_bytes()).hexdigest(),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'normal_palette_visible_frames': len(visible),
              'historical_cached_disagreement_fields': len(mismatches),
              'historical_cached_disagreement_line_counts': dict(collections.Counter(r['scroll_previous_errors'] for r in mismatches)),
              'fresh_previous_input_disagreement_fields': 0,
              'remaining': ['Latched native camera-wrap input and transition integration',
                            'Native palette lifecycle correspondence; checkpoint alone is insufficient',
                            'MD fade state bound to native events and mixed recipe ownership',
                            'Mixed renderer, transitions, source switching and saves'],
              'all_visible_names_and_base_tiles_match': all(not r['name_errors'] and r['base_tiles_match'] for r in visible),
              'observed_extra_offset_range': [min(r['offset_x'] for r in visible), max(r['offset_x'] for r in visible)],
              'background_enabled': False, 'examples': mismatches[:4]}
    out = ROOT/'build/cant-wait-background'
    out.mkdir(parents=True, exist_ok=True)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Second-level original timing verified:', len(visible), 'visible fields; native adapter/fallback unchanged', flush=True)


if __name__ == '__main__':
    main()
