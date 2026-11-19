"""Observe original MD palette writers during the second-level reference.

Run with the embedded 32-bit Python and the research-only trace DLL. Unmodified
ordinary controller replay must reproduce retained WRAM and original pictures.
This does not enable or certify a mixed scene renderer.
"""
import collections
import csv
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png
from md_scene_background import palette_transition_step


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'build/md-next-levels-replay'
    out = ROOT/'build/cant-wait-palette'
    out.mkdir(parents=True, exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING', 'scope': __doc__})+'\n')
    rows = json.loads((source/'frames.json').read_text())
    rom = (ROOT/'Lion King, The (World).md').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    palettes = [rom[a:a+128] for a in (0x1ea604, 0x1ea684)]
    game = MdLab()
    trace = C.CDLL(str(ROOT/'build/md_cant_wait_trace.dll'))
    trace.md_cant_wait_trace_init.argtypes = [C.c_void_p, C.c_char_p]
    assert trace.md_cant_wait_trace_init(game.core._handle, str(out/'writers.csv').encode())
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    game.core.retro_set_controller_port_device(0, 513)
    game.core.retro_set_controller_port_device(1, 513)
    snapshots = 0
    pictures = []
    changes = []
    previous = None
    try:
        for row in rows[:13101]:
            frame = row['frame']
            trace.md_cant_wait_trace_frame(frame)
            game.step(row['pad'])
            if row['level'] == 1:
                # Convert the core's word-swapped memory to ROM byte order.
                raw = bytes(game.cram)
                colors = b''.join(raw[i:i+2][::-1] for i in range(0, len(raw), 2))
                # CRAM stores compact 9-bit colors rather than original words.
                values = list(struct.unpack('<64H', raw))
                expected = [[(c>>1&7)|((c>>5&7)<<3)|((c>>9&7)<<6)
                             for c in struct.unpack('>64H', p)] for p in palettes]
                variants = [i for i,p in enumerate(expected) if values[16:32] == p[16:32]]
                complete_variants = [i for i,p in enumerate(expected) if values == p]
                key = (tuple(variants), hashlib.sha256(colors).hexdigest())
                if key != previous:
                    changes.append({'frame': frame, 'background_palette_variants': variants,
                                    'complete_cram_palette_variants': complete_variants,
                                    'cram_sha256': key[1],
                                    'checkpoint': struct.unpack_from('<HH', bytes(game.work_ram), 0xccd6)})
                    previous = key
            if frame % 100 == 1 and (source/f'{frame:05d}-wram.bin').exists():
                assert bytes(game.work_ram) == (source/f'{frame:05d}-wram.bin').read_bytes(), ('Original WRAM changed', frame)
                snapshots += 1
            if frame in (6000, 8000, 10000, 12000):
                path = out/f'{frame}.png'
                png(path, *game.image)
                assert path.read_bytes() == (source/f'capture-{frame}/screen.png').read_bytes(), ('Original picture changed', frame)
                pictures.append(frame)
            if frame % 2000 == 0:
                print('Original palette replay field', frame, flush=True)
            game.samples.clear()
    finally:
        trace.md_cant_wait_trace_close()
        game.close()
    events = list(csv.DictReader((out/'writers.csv').open()))
    entries = [r for r in events if r['type'] == '1']
    writers = collections.Counter(r['pc'] for r in events if r['type'] == '4')
    assert writers and entries and snapshots > 100 and len(pictures) == 4
    fade_writes = [r for r in events if r['type'] == '4' and r['pc'] == '18d816']
    passes = collections.defaultdict(list)
    targets = collections.Counter()
    for row in fade_writes:
        pointer = int(row['a0'], 16)-2
        assert 0 <= pointer < len(rom)-1
        target = int.from_bytes(rom[pointer:pointer+2], 'big')
        expected = palette_transition_step(int(row['before'], 16), target)
        assert int(row['value'], 16) == expected, ('Original fade differs', row)
        address = int(row['address'], 16)
        passes[int(row['frame'])].append(address)
        targets[pointer-(address-0xff845c)] += 1
    assert len(fade_writes) > 30000
    assert all(addresses == list(range(0xff845c, 0xff8524, 2)) for addresses in passes.values()), 'Incomplete original software palette pass'
    report = {'result': 'OBSERVED_PENDING_NATIVE_MAPPING', 'scope': __doc__,
              'rom_sha256': hashlib.sha256(rom).hexdigest(),
              'core_sha256': digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
              'trace_dll_sha256': digest(ROOT/'build/md_cant_wait_trace.dll'),
              'trace_source_sha256': digest(ROOT/'tools/md_cant_wait_trace.c'),
              'palette_recipe_source_sha256': digest(ROOT/'tools/md_scene_background.py'),
              'input_reference_sha256': digest(source/'frames.json'),
              'writers_csv_sha256': digest(out/'writers.csv'),
              'unchanged_wram_snapshots': snapshots, 'unchanged_picture_fields': pictures,
              'original_entries': entries, 'palette_writer_pc_counts': dict(writers),
              'original_palette_step_writes_matched': len(fade_writes),
              'original_complete_100_color_passes': len(passes),
              'original_palette_targets': {hex(k): v for k,v in targets.items()},
              'palette_changes': changes, 'palette_scope': 'All 64 CRAM colors and all 100 software fade destinations',
              'background_enabled': False,
              'remaining': ['Identify transition-object lifecycle and native counterpart',
                            'Implement dynamic scene hydration and verified mixed rendering']}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Original palette writers observed:', dict(writers), '; pictures and', snapshots, 'WRAM snapshots unchanged', flush=True)


if __name__ == '__main__':
    main()
