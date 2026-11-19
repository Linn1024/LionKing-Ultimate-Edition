"""Observe original MD title Start readiness after a genuine Game Over timeout."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from md_lab import ROOT, MdLab, png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT / 'build/pride-game-over-title-input-original'
    out.mkdir()
    reference = ROOT / 'build/pride-game-over-exits-original/report.json'
    bound(reference)
    state = reference.parent / 'prefatal.state'
    blob = C.create_string_buffer(state.read_bytes())
    inputs = ROOT / 'build/pride-final-arena-original/inputs.json'
    fatal_pad = json.loads(inputs.read_text())[4598 - 1]
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1):
        game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
    game.core.retro_unserialize.restype = C.c_bool
    cases = {}
    try:
        for pressed in [None, 400, 500, 600, 700, 800, 1000, 1400]:
            name = 'neutral' if pressed is None else f'start{pressed}'
            folder = out / name
            folder.mkdir()
            assert game.core.retro_unserialize(blob, state.stat().st_size)
            rows = []
            for age in range(2001):
                pad = fatal_pad if age == 0 else (8 if pressed is not None and pressed <= age < pressed + 4 else 0)
                game.step(pad)
                game.samples.clear()
                if age % 50 == 0 or age in (370, 463):
                    data, w, h, pitch, fmt = game.image
                    tight = b''.join(data[y*pitch:y*pitch+w*2] for y in range(h))
                    word = lambda at: game.work_ram[at] | game.work_ram[at+1] << 8
                    rows.append(dict(age=age, picture_sha256=hashlib.sha256(tight).hexdigest(),
                                     level=word(0xccce), health=word(0xccf6), lives=word(0xccee), credits=word(0xccda)))
                if age in (700, 1000, 1400, 2000):
                    png(folder / f'{age}.png', *game.image)
            cases[name] = dict(pressed_age=pressed, held_fields=4 if pressed is not None else 0, frames=rows)
            print(name, rows[-1], flush=True)
    finally:
        game.close()
    neutral = {row['age']: row['picture_sha256'] for row in cases['neutral']['frames']}
    for name, case in cases.items():
        case['first_sample_picture_differs_from_neutral'] = next((r['age'] for r in case['frames']
            if case['pressed_age'] is not None and r['age'] >= case['pressed_age'] and r['picture_sha256'] != neutral[r['age']]), None)
    paths = [Path(__file__), reference, state, inputs, ROOT / 'tools/md_lab.py', ROOT / 'Lion King, The (World).md']
    report = dict(result='OBSERVED', ordinary_route=True, guest_or_rom_edits=False, cases=cases,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
