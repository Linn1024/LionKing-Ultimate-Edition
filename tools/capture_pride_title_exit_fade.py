"""Capture original MD outgoing NO/timeout frames and test frozen-canvas fades."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab, png
from pride_arena_history import bound
from verify_windows import pixels


def main():
    out = ROOT/'build/pride-title-exit-fade-reference'
    out.mkdir()
    reference = ROOT/'build/pride-final-input-reference/report.json'
    bound(reference)
    state = reference.parent/'prefatal.state'
    data = state.read_bytes()
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1):
        game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
    game.core.retro_unserialize.restype = C.c_bool
    observations = {}
    levels = [[0,32,65,98,139,172,205,238], [0,32,68,101,137,170,206,238], [0,32,65,98,139,172,205,238]]
    try:
        for name, origin in [('no', 140), ('timeout', 844)]:
            folder = out/name
            folder.mkdir()
            blob = C.create_string_buffer(data)
            assert game.core.retro_unserialize(blob, len(data))
            for age in range(origin+23):
                pad = 128 if age == 0 else 0
                if name == 'no':
                    if 130 <= age <= 133:
                        pad = 128
                    elif 140 <= age <= 143:
                        pad = 256
                game.step(pad)
                game.samples.clear()
                if age >= origin-1:
                    png(folder/f'{age}.png', *game.image)
            candidates = {}
            for start in (origin-1, origin, origin+1):
                source = pixels(folder/f'{start}.png')[2]
                indexed = [tuple(levels[c].index(p[c]) for c in range(3)) for p in source]
                errors = {}
                for age in range(origin, origin+23):
                    actual = pixels(folder/f'{age}.png')[2]
                    loss = max(0, (age-origin+2)//3)
                    wrong = sum(any(levels[c][max(0, p[c]-loss)] != q[c] for c in range(3))
                                for p, q in zip(indexed, actual))
                    if wrong:
                        errors[str(age)] = wrong
                candidates[str(start)] = errors
            observations[name] = dict(origin=origin, candidate_frozen_source_errors=candidates)
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
