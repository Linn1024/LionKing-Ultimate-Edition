"""Trace the unmodified MD second-level scroll callback during ordinary play.

Replay the recorded controller values from the existing unforced reference.
Observe callback inputs, all 224 completed RAM words and the final VDP table;
no CPU registers, game RAM or cartridge bytes are changed.
Run with .tools/python32/python.exe after building md_scene_trace.dll.
"""
import csv
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png
from md_scene_background import line_offsets


def main():
    source = ROOT/'build/md-next-levels-replay'
    out = ROOT/'build/cant-wait-timing'
    out.mkdir(parents=True, exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result': 'RUNNING', 'scope': __doc__})+'\n')
    rows = json.loads((source/'frames.json').read_text())
    game = MdLab()
    trace = C.CDLL(str(ROOT/'build/md_scene_trace.dll'))
    trace.md_scene_trace_init.argtypes = [C.c_void_p, C.c_char_p]
    assert trace.md_scene_trace_init(game.core._handle, str(out/'callbacks.csv').encode())
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    game.core.retro_set_controller_port_device(0, 513)
    game.core.retro_set_controller_port_device(1, 513)
    vdp = {}
    image_checks = []
    ram_checks = 0
    try:
        for row in rows[:13101]:
            frame = row['frame']
            trace.md_scene_trace_frame(frame)
            game.step(row['pad'])
            if row['level'] == 1:
                base = (game.reg[13]&63)<<10
                vdp[frame] = [struct.unpack_from('<H', bytes(game.vram), (base+y*4+2)&65535)[0]&1023 for y in range(224)]
            if frame in (6000, 8000, 10000, 12000):
                capture = out/f'{frame}.png'
                png(capture, *game.image)
                assert capture.read_bytes() == (source/f'capture-{frame}/screen.png').read_bytes(), ('Picture changed', frame)
                image_checks.append(frame)
            if frame % 2000 == 0:
                print('Original replay field', frame, flush=True)
            # Observational hooks must preserve the previously captured execution.
            snapshot = source/f'{frame:05d}-wram.bin'
            if frame % 100 == 1 and snapshot.exists():
                assert bytes(game.work_ram) == snapshot.read_bytes(), ('Replay changed', frame)
                ram_checks += 1
            game.samples.clear()
    finally:
        trace.md_scene_trace_close()
        game.close()
    entries = {}
    tables = []
    for fields in csv.reader((out/'callbacks.csv').open()):
        frame, pc, level, camera, extra, argument = [int(v, 16 if i == 1 else 10) for i, v in enumerate(fields[:6])]
        if pc == 0x8bb3a:
            entries[frame] = (camera, extra, argument)
        else:
            assert frame in entries
            camera, extra, argument = entries[frame]
            assert argument == (camera+extra)&65535
            actual = [int(v)&1023 for v in fields[6:]]
            expected = [(-v)&1023 for v in line_offsets(1, argument)]
            assert actual == expected, ('Callback arithmetic differs', frame, argument)
            tables.append((frame, actual, camera, extra))
    observations = {r['frame']: r for r in json.loads((source/'scene-backgrounds.json').read_text()) if r['level'] == 1}
    visible = {f for f,r in observations.items() if r['display_enabled'] and r['normal_background_palette_variants']}
    matches = []
    gaps = []
    previous_input_gaps = []
    for frame in sorted(visible):
        # The saved audit reports positive source offsets; VDP words store
        # their ten-bit two's-complement displacement.
        assert all(vdp[frame][y] == ((-value)&1023) for y, value in observations[frame]['scroll_bands']), ('Stored VDP samples changed', frame)
        candidates = [(f, camera, extra) for f, words, camera, extra in tables
                      if f <= frame and vdp.get(frame) == words]
        candidates = candidates[-4:]
        if candidates:
            matches.append({'frame': frame, 'callback_inputs': candidates})
        else:
            gaps.append(frame)
        prior = observations.get(frame-1)
        if prior and vdp[frame] != [(-v)&1023 for v in line_offsets(1, prior['input_x'])]:
            previous_input_gaps.append(frame)
    report = {'result': 'PASS' if not gaps and not previous_input_gaps else 'PARTIAL', 'scope': __doc__,
              'source_sha256': hashlib.sha256((source/'frames.json').read_bytes()).hexdigest(),
              'callback_count': len(tables), 'all_callback_arithmetic_matches': True,
              'trace_sha256': hashlib.sha256((out/'callbacks.csv').read_bytes()).hexdigest(),
              'rom_sha256': hashlib.sha256((ROOT/'Lion King, The (World).md').read_bytes()).hexdigest(),
              'unchanged_wram_snapshot_checks': True,
              'unchanged_wram_snapshot_count': ram_checks,
              'all_stored_visible_scroll_samples_unchanged': True,
              'unchanged_original_picture_fields': image_checks,
              'visible_fields': len(visible), 'matched_vdp_fields': len(matches),
              'unmatched_fields': gaps, 'previous_input_unmatched_fields': previous_input_gaps,
              'background_enabled': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    (out/'vdp-matches.json').write_text(json.dumps(matches, separators=(',', ':'))+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
