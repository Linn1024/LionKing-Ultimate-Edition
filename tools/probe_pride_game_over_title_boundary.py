"""Find the original MD post-Game-Over title fresh-Start boundary without edits."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT, MdLab, png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def picture(game):
    data, w, h, pitch, fmt = game.image
    assert (w, h, fmt) == (320, 224, 2)
    return hashlib.sha256(b''.join(data[y*pitch:y*pitch+w*2] for y in range(h))).hexdigest()


def main():
    out = ROOT / 'build/pride-game-over-title-boundary-original'; out.mkdir()
    reference = ROOT / 'build/pride-game-over-title-input-original/report.json'; bound(reference)
    state = ROOT / 'build/pride-game-over-exits-original/prefatal.state'
    blob = C.create_string_buffer(state.read_bytes())
    inputs = ROOT / 'build/pride-final-arena-original/inputs.json'
    fatal_pad = json.loads(inputs.read_text())[4598-1]
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1): game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]; game.core.retro_unserialize.restype = C.c_bool
    game.core.retro_serialize_size.restype = C.c_size_t
    game.core.retro_serialize.argtypes = [C.c_void_p, C.c_size_t]; game.core.retro_serialize.restype = C.c_bool
    cases = {}; checks = {}
    try:
        assert game.core.retro_unserialize(blob, len(blob)-1)
        for age in range(500):
            game.step(fatal_pad if age == 0 else 0); game.samples.clear()
        n = game.core.retro_serialize_size(); checkpoint = C.create_string_buffer(n)
        assert game.core.retro_serialize(checkpoint, n)
        (out / 'neutral499.state').write_bytes(checkpoint.raw)
        neutral = {}
        for age in range(500, 1201):
            game.step(0); game.samples.clear(); neutral[age] = picture(game)
            if age == 630: png(out / 'neutral630.png', *game.image)
        for duration in (1, 4):
            rows = []
            for pressed in range(500, 601):
                assert game.core.retro_unserialize(checkpoint, n)
                first_diff = None
                for age in range(500, 631):
                    game.step(8 if pressed <= age < pressed+duration else 0); game.samples.clear()
                    if first_diff is None and picture(game) != neutral[age]: first_diff = age
                rows.append(dict(pressed=pressed, duration=duration, first_picture_difference=first_diff, picture630=picture(game)))
            first = next(r['pressed'] for r in rows if r['first_picture_difference'] is not None)
            checks[f'{duration}_single_boundary'] = all((r['first_picture_difference'] is not None) == (r['pressed'] >= first) for r in rows)
            cases[str(duration)] = dict(first_accepted=first, probes=rows)
            for pressed in (first-1, first):
                assert game.core.retro_unserialize(checkpoint, n)
                folder = out / f'hold{duration}-start{pressed}'; folder.mkdir()
                for age in range(500, 1201):
                    game.step(8 if pressed <= age < pressed+duration else 0); game.samples.clear()
                    if age in (630, 1000, 1200): png(folder / f'{age}.png', *game.image)
                cases[str(duration)][str(pressed)] = dict(picture1200=picture(game), same_as_neutral1200=picture(game) == neutral[1200])
            checks[f'{duration}_early_no_later_effect'] = cases[str(duration)][str(first-1)]['same_as_neutral1200']
            checks[f'{duration}_accepted_later_effect'] = not cases[str(duration)][str(first)]['same_as_neutral1200']
            print(duration, 'first accepted', first, flush=True)
    finally: game.close()
    paths = [Path(__file__), reference, state, inputs, ROOT / 'tools/md_lab.py', ROOT / 'Lion King, The (World).md']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, cases=cases,
                  guest_or_rom_edits=False, ordinary_route=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert all(checks.values())


if __name__ == '__main__': main()
