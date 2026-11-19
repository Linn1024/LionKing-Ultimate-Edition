"""Verify the ROM-backed second-level recipe and cache-v1 hydration.

Original plane pixels, palette writer fixtures and isolated original arithmetic
are separate evidence. None establishes the unfinished native timing adapter.
Prepare references with cant_wait_background_reference.py (32-bit Python) and
md_scene_scroll_audit.py, then build tlk_cant_wait_background_test.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import struct
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/cant-wait-renderer'
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING'})+'\n')
    reference_path = out/'reference.json'
    reference = json.loads(reference_path.read_text())
    assert reference['result'] == 'PASS' and reference['pixels'] == 573440
    assert reference['palette_passes'] == 398 and reference['palette_writes'] == 39800
    bindings = [('frames_source_sha256', ROOT/'build/md-next-levels-replay/frames.json'),
                ('rom_sha256', ROOT/'Lion King, The (World).md'),
                ('core_sha256', ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
                ('palette_report_sha256', ROOT/'build/cant-wait-palette/report.json'),
                ('writers_sha256', ROOT/'build/cant-wait-palette/writers.csv'),
                ('pixel_fixture_sha256', out/'original-pixels.bin'),
                ('fade_fixture_sha256', out/'original-fades.bin'),
                ('exporter_sha256', ROOT/'tools/cant_wait_background_reference.py')]
    for key, path in bindings:
        assert reference[key] == digest(path), ('Stale original reference', key)
    scroll_path = ROOT/'build/md-scene-scroll-oracle/line-scroll.bin'
    scroll_report = json.loads((scroll_path.parent/'report.json').read_text())
    assert scroll_report['result'] == 'PASS' and scroll_report['cases'] == 316
    cache = ROOT/'game-data/scenes-v1.cache'
    cache_hash = digest(cache)
    header = cache.read_bytes()[:112]
    assert header[:8] == b'TLKSCN01' and struct.unpack_from('<I', header, 8)[0] == 1
    test = ROOT/'engine/build-win/tlk_cant_wait_background_test.exe'
    command = [test, ROOT/'Lion King, The (World).md', ROOT/'Lion King, The (USA).sfc',
               cache, out/'original-pixels.bin', out/'original-fades.bin', scroll_path]
    log_path = out/'unit.log'
    with log_path.open('wb') as log:
        subprocess.run(list(map(str, command)), cwd=ROOT, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=60)
    log = log_path.read_text()
    assert 'cant_wait_background_test: PASS (0 failed)' in log
    assert log.count('573440 pixels, 0 mismatches') == 2
    assert log.count('39800 writes, 0 mismatches') == 2
    assert '158 cases x224 lines, 0 mismatches' in log
    assert digest(cache) == cache_hash, 'Existing installation cache was changed'
    sources = ['engine/runner/tlk_md_assets.c', 'engine/runner/tlk_md_assets.h',
               'engine/runner/tlk_resources.c', 'engine/tests/cant_wait_background_test.c',
               'tools/verify_cant_wait_renderer.py']
    report = {'result': 'ORIGINAL_RENDERER_VERIFIED_PENDING_NATIVE_ADAPTER', 'scope': __doc__,
              'reference_sha256': digest(reference_path), 'test_sha256': digest(test),
              'player_sha256': digest(ROOT/'dist/LionKing.exe'),
              'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'source_sha256': {name: digest(ROOT/name) for name in sources},
              'log_sha256': digest(log_path), 'scroll_fixture_sha256': digest(scroll_path),
              'original_pixels_per_initialization': 573440, 'original_fade_writes_per_initialization': 39800,
              'original_arithmetic_cases': 158, 'initialization_paths': ['ROM decode', 'existing cache-v1 plus ROM hydration'],
              'installed_cache_sha256': cache_hash, 'installed_cache_unchanged': True,
              'scene_1_static_ready': False, 'mixed_background_enabled': False,
              'remaining': ['Native palette transition timing and target ownership',
                            'Latch native camera plus wrap at the displayed field',
                            'Mixed priority/occlusion, transitions, source switching and moving saves']}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Second-level C recipe PASS: 573440 original pixels, 39800 fade writes, 158 arithmetic cases;',
          'both decode/cache hydration pass; native integration remains open', flush=True)


if __name__ == '__main__':
    main()
