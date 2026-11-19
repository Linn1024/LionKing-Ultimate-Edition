"""Capture ordinary original MD Continue NO and timeout exits."""
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
    out = ROOT/'build/pride-final-menu-exits-reference'
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
    trace = C.CDLL(str(ROOT/'build/md_commands.dll'))
    trace.md_commands_init.argtypes = [C.c_void_p, C.c_char_p]
    observations = {}
    fatal = 14788
    try:
        for name in ('no', 'timeout'):
            folder = out/name
            folder.mkdir()
            blob = C.create_string_buffer(data)
            assert game.core.retro_unserialize(blob, len(data))
            assert trace.md_commands_init(game.core._handle, str(folder/'commands.csv').encode())
            captures = []
            for age in range(1601):
                pad = 128 if age == 0 else 0
                if name == 'no':
                    if 130 <= age <= 133:
                        pad = 128
                    elif 140 <= age <= 143:
                        pad = 256
                trace.md_commands_frame(fatal+age)
                game.step(pad)
                game.samples.clear()
                if age in (100, 124, 140, 180, 300, 600, 1000, 1600):
                    png(folder/f'{age}.png', *game.image)
                    word = lambda at: game.work_ram[at] | game.work_ram[at+1] << 8
                    captures.append(dict(age=age, health=word(0xccf6), lives=word(0xccee), level=word(0xccce)))
            trace.md_commands_close()
            rows = list(csv.DictReader((folder/'commands.csv').open()))
            music = [dict(age=int(row['frame'])-fatal, program=int(row['value']))
                     for row in rows if row['selector'] == '1']
            observations[name] = dict(captures=captures, music=music)
            print(name, music, flush=True)
    finally:
        game.close()
    paths = [Path(__file__), reference, state, ROOT/'tools/md_lab.py',
             ROOT/'build/md_commands.dll', ROOT/'Lion King, The (World).md']
    report = dict(result='OBSERVED', observations=observations,
                  no_guest_or_rom_edits=True, source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
