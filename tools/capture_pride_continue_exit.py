"""Observe Continue exit pictures and real player ownership, without guest edits.

Run with the pinned Python32. Outputs are excluded local research artifacts.
"""
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab, png
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-continue-exit-observation'
    out.mkdir()
    ages = (124, 130, 145, 160, 165, 179, 200, 240, 400, 600)
    md = out/'md'; md.mkdir()
    origin = ROOT/'build/pride-final-input-reference/prefatal.state'
    raw = origin.read_bytes(); state = C.create_string_buffer(raw)
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1): game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
    game.core.retro_unserialize.restype = C.c_bool
    owned = []
    try:
        assert game.core.retro_unserialize(state, len(raw))
        word = lambda a: game.work_ram[a] | game.work_ram[a+1] << 8
        for age in range(801):
            game.step(128 if age == 0 else (256 if age == 124 else 0))
            game.samples.clear()
            camera = word(0xcd36)
            player = word(camera+0x36) if 0x8000 <= camera < 0xffc8 else 0
            if 0x8000 <= player < 0xffc0:
                owned.append(dict(age=age, camera=camera, player=player,
                                  x=word(player+8), y=word(player+12), health=word(0xccf6)))
            if age in ages:
                png(md/f'{age}.png', *game.image)
                (md/f'{age}-wram.bin').write_bytes(bytes(game.work_ram))
    finally:
        game.close()
    base = ROOT/'build/pride-final-input-refresh-probe2'
    build = bound(base/'build-report.json'); binary = base/'player.exe'
    assert digest(binary) == build['binary_sha256']
    fixture_path = ROOT/'build/pride-final-continue-fixture/report.json'
    fixture = bound(fixture_path); fatal = fixture['fatal_field']
    original = (fixture_path.parent/'neutral-after-final.tape').read_bytes()
    native = out/'native'; native.mkdir()
    profile = out/'resources.ini'; profile.write_text('schema = 1\ngame = snes\n')
    config = out/'host.ini'; config.write_text('opengl = 0\nscale = 2\n')
    tape = out/'confirm124.tape'
    tape.write_bytes(original[:fatal*2]+struct.pack('<800H', *[0x8000 if n == 124 else 0 for n in range(1, 801)]))
    clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    observations = []; commands = []
    for age in ages:
        folder = native/str(age); folder.mkdir()
        cmd = list(map(str, [binary, '--rom', ROOT/'Lion King, The (USA).sfc',
            '--md-rom', ROOT/'Lion King, The (World).md', '--resource-profile', profile,
            '--config', config, '--load', fixture_path.parent/'prefatal.state',
            '--input', tape, '--lle', '--frames', fatal+age, '--no-pace', '--no-audio',
            '--no-record', '--dump-window', folder/'window.png', '--dump-scene', folder/'scene.json']))
        env = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1',
            TLK_FINAL_FAST_ASSETS='1', TLK_FINAL_SCENE_PRESENT='1',
            TLK_FINAL_SKIP_LOG=str(folder/'points.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=240, creationflags=subprocess.CREATE_NO_WINDOW)
        scene = json.loads((folder/'scene.json').read_text())
        row = dict(age=age, gameplay=scene['latched_gameplay'])
        observations.append(row); commands.append(cmd); print(row, flush=True)
    paths = [Path(__file__), origin, base/'build-report.json', binary, fixture_path]
    report = dict(result='OBSERVED', original_owned_player=owned,
        native_observations=observations, commands=commands, public_player_changed=False,
        readiness_requires_live_player_and_control=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('OBSERVED', len(owned), 'MD fields with camera/player link', flush=True)


if __name__ == '__main__': main()
