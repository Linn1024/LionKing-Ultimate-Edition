"""Observe original MD timeout precedence and direction changes at Continue."""
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
    out = ROOT/'build/pride-continue-timeout-last-edge'
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
    trace = C.CDLL(str(ROOT/'build/md_commands.dll'))
    trace.md_commands_init.argtypes = [C.c_void_p, C.c_char_p]
    cases = {'neutral': {}, **{f'confirm{age}': {age: 256} for age in (845, 846, 847, 848, 850, 855, 860, 865, 870, 874, 875)}}
    observations = {}
    try:
        for name, pads in cases.items():
            folder = out/name
            folder.mkdir()
            assert game.core.retro_unserialize(blob, state.stat().st_size)
            assert trace.md_commands_init(game.core._handle, str(folder/'commands.csv').encode())
            timers = {}
            for age in range(1301):
                trace.md_commands_frame(14788+age)
                game.step(128 if age == 0 else pads.get(age, 0))
                game.samples.clear()
                if age in (122, 123, 124, 125, 199, 200, 201, 399, 400, 401, 841, 842, 843, 844, 845):
                    timers[str(age)] = int.from_bytes(bytes(game.work_ram[0xfff4:0xfff6]), 'little')
                if age in (900, 1300):
                    png(folder/f'{age}.png', *game.image)
            trace.md_commands_close()
            rows = list(csv.DictReader((folder/'commands.csv').open()))
            music = [dict(age=int(row['frame'])-14788, program=int(row['value']))
                     for row in rows if row['selector'] == '1']
            observations[name] = dict(pads=pads, timer_candidate=timers, music=music)
            print(name, music, flush=True)
    finally:
        game.close()
    checks = {name: ('continued' if any(r['program'] == 137 for r in row['music']) else 'title') for name, row in observations.items()}
    paths = [Path(__file__), reference, state, ROOT/'tools/md_lab.py', ROOT/'build/md_commands.dll']
    report = dict(result='OBSERVED', observations=observations, observed_outcomes=checks,
                  no_guest_or_rom_edits=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(checks, flush=True)


if __name__ == '__main__':
    main()
