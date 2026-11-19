"""Record original MD NO/timeout black and title appearance boundaries."""
import array
import ctypes as C
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab, png
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-final-title-phases'
    out.mkdir()
    reference = ROOT/'build/pride-final-input-reference/report.json'
    bound(reference)
    state = reference.parent/'prefatal.state'
    blob = C.create_string_buffer(state.read_bytes())
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1):
        game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
    game.core.retro_unserialize.restype = C.c_bool
    observations = {}
    try:
        for name, decision in [('no', 140), ('timeout', 845)]:
            folder = out/name
            folder.mkdir()
            assert game.core.retro_unserialize(blob, state.stat().st_size)
            rows = []
            black = first_title = None
            for age in range(decision+301):
                pad = 128 if age == 0 else 0
                if name == 'no':
                    if 130 <= age <= 133:
                        pad = 128
                    elif 140 <= age <= 143:
                        pad = 256
                game.step(pad)
                game.samples.clear()
                raw, width, height, pitch, fmt = game.image
                assert fmt == 2, fmt
                values = array.array('H')
                values.frombytes(b''.join(raw[y*pitch:y*pitch+width*2] for y in range(height)))
                lit = width*height-values.count(0)
                rows.append(dict(age=age, width=width, height=height, lit=lit))
                if age > decision and lit == 0 and black is None:
                    black = age
                if black is not None and age > black and lit > 0 and first_title is None:
                    first_title = age
                    png(folder/'first-title.png', *game.image)
                if age in (decision, decision+20, decision+40, decision+60, decision+100, decision+160, decision+300):
                    png(folder/f'{age}.png', *game.image)
            with (folder/'frames.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=['age', 'width', 'height', 'lit'])
                writer.writeheader()
                writer.writerows(rows)
            observations[name] = dict(decision=decision, first_black=black, first_title_pixels=first_title)
            print(name, observations[name], flush=True)
    finally:
        game.close()
    paths = [Path(__file__), reference, state, ROOT/'tools/md_lab.py']
    report = dict(result='OBSERVED', observations=observations, no_guest_or_rom_edits=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
