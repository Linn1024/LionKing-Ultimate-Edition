"""Execute original native palette-trigger fixtures, separate from live replay.

This proves the trigger's conditional DMA request, not displayed palette timing,
normal actor reachability, MD fade-clock correspondence or full mixed rendering.
Run with embedded32 Python after building cant_wait_native_palette.dll.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/cant-wait-native-palette'
    out.mkdir(parents=True, exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING'})+'\n')
    rom = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    path = ROOT/'build/cant_wait_native_palette.dll'
    library = C.CDLL(str(path))
    library.terrain_native_init.argtypes = [C.c_void_p, C.c_uint]
    assert library.terrain_native_init(C.create_string_buffer(rom), len(rom))
    library.cant_wait_palette_trigger.argtypes = [C.c_uint]*3+[C.POINTER(C.c_uint)]
    result = (C.c_uint*7)()
    cases = triggered = skipped = 0
    def check(x, y, started):
        nonlocal cases, triggered, skipped
        assert library.cant_wait_palette_trigger(x, y, started, result), (x, y, started)
        fires = not started and (x >= 108 or y >= 480)
        expected = [1, 0xc601b5, 0x200, 0, 1, 0x1ff0] if fires else [started, 0xefabcd, 0x1234, 0x56, 0x789a, 0x1ff0]
        assert list(result)[:6] == expected, (x, y, started, list(result))
        cases += 1
        triggered += bool(fires)
        skipped += not fires
    # All sixteen-bit coordinates on either side of both branch boundaries,
    # plus every already-started flag value at positions that would trigger.
    for coordinate in range(65536):
        for y in (0, 479, 480, 65535):
            check(coordinate, y, 0)
        for x in (0, 107, 108, 65535):
            check(x, coordinate, 0)
        check(65535, 65535, coordinate)
    report = {'result': 'TRIGGER_VERIFIED_DISPLAY_TIMING_OPEN', 'scope': __doc__,
              'cases': cases, 'triggered': triggered, 'skipped': skipped,
              'original_entry': 'C0D178', 'stop_before': 'C0D1AC',
              'condition': 'A4A == 0 and (actor X >= 108 or actor Y >= 480), unsigned16',
              'request': {'palette': 'C601B5', 'cgram_start_C8': 0, 'DMA_bytes_C6': 512, 'pending_CA': 1},
              'stack_preserved': True, 'live_gameplay_mutated': False,
              'source_sha256': {name: digest(ROOT/name) for name in (
                  'tools/cant_wait_native_palette_oracle.c', 'tools/pride_terrain_native_oracle.c',
                  'tools/audit_cant_wait_native_palette.py', 'engine/snesrecomp/runner/src/snes/interp816.c',
                  'engine/build-win/tlk-runtime/interp816.c')},
              'oracle_sha256': digest(path), 'rom_sha256': hashlib.sha256(rom).hexdigest(),
              'mixed_background_enabled': False}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Original native palette trigger:', cases, 'cases PASS; displayed timing remains open', flush=True)


if __name__ == '__main__':
    main()
