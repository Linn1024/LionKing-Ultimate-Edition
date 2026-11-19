"""Capture ordinary Options/new-game starting resources in both originals.

This establishes starting lives/health only, not enemy or damage difficulty.
MD runs with embedded 32-bit Python; SNES uses the actual Windows public player.
No loaded states, practice menu, guest edits or cartridge patches are used.
"""
import argparse
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', choices=('snes', 'md'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), ROOT/'tools/md_lab.py']
    observations = {}
    if args.source == 'md':
        from md_lab import MdLab, png
        source = ROOT/'build/md-next-levels-replay/frames.json'
        inputs = json.loads(source.read_text())
        rom = ROOT/'Lion King, The (World).md'
        assert digest(rom) == 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
        paths += [source, rom, ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
        for name, button in [('easy', 64), ('normal', 0), ('hard', 128)]:
            folder = out/name
            folder.mkdir()
            game = MdLab()
            game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
            for port in (0, 1):
                game.core.retro_set_controller_port_device(port, 513)
            pads = []
            try:
                # Let the changed Options label render before the recorded Start.
                for field in range(1, 1411):
                    original = field if field <= 1000 else field-10
                    pad = (button if field == 1000 else 0 if field <= 1010 and field > 1000
                           else inputs[original-1]['pad'])
                    pads.append(pad)
                    game.step(pad)
                    game.samples.clear()
                    if field in (1010, 1410):
                        png(folder/f'{field}.png', *game.image)
                ram = bytes(game.work_ram)
                (folder/'wram.bin').write_bytes(ram)
                word = lambda address: struct.unpack_from('<H', ram, address)[0]
                observations[name] = dict(health=word(0xccf6), lives=word(0xccee),
                                          level=word(0xccce), field=1410)
                assert observations[name]['level'] == 1
            finally:
                game.close()
            (folder/'inputs.json').write_text(json.dumps(pads)+'\n')
    else:
        sys.path.insert(0, str(ROOT/'engine/tools'))
        import make_play_tapes as macros
        exe = ROOT/'build/pride-arena-work/tlk_pride_player.exe'
        rom = ROOT/'Lion King, The (USA).sfc'
        assert digest(exe) == '979a74691586e228d0ed253f637f04760eef86a2fb87a64b66614b65ac250df2'
        assert digest(rom) == '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
        paths += [exe, rom, ROOT/'engine/tools/make_play_tapes.py', ROOT/'engine/tools/re/make_level_tape.py']
        env = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
        for name, presses in [('easy', 2), ('normal', 0), ('hard', 1)]:
            folder = out/name
            folder.mkdir()
            words = macros.t_difficulty(presses, play=0)
            tape = folder/'ordinary.tape'
            tape.write_bytes(struct.pack('<'+'H'*len(words), *words))
            profile = folder/'resources.ini'
            profile.write_text('schema = 1\ngame = snes\n')
            config = folder/'host.ini'
            config.write_text('opengl = 0\nscale = 2\n')
            cmd = [exe, '--rom', rom, '--resource-profile', profile, '--config', config,
                   '--input', tape, '--frames', str(len(words)), '--no-pace', '--no-audio',
                   '--no-record', '--dump-scene', folder/'scene.json',
                   '--dump-window', folder/'window.png', '--dump-png', folder/'guest.png']
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=180)
            scene = json.loads((folder/'scene.json').read_text())
            guest = scene['latched_gameplay']
            assert scene['level'] == 0 and guest['descriptor'] == 0x387
            observations[name] = dict(health=guest['health'], lives=guest['lives'],
                                      level=scene['level'], field=len(words))
    report = dict(result='CAPTURED', scope=__doc__, source=args.source,
                  ordinary_power_on=True, loaded_states=False, guest_or_rom_edits=False,
                  observations=observations,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix():digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(args.source, observations, flush=True)


if __name__ == '__main__':
    main()
