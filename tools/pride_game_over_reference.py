"""Observe original Pride game-over music using ordinary controls only.

Replay the retained original movie prefix4000, neutral through5400, then hold
Right until all lives expire. No state, cartridge, actor, health/lives/RNG edits.
Run using embedded32 Python and the observational MD commands DLL.
"""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/pride-game-over-original'
    out.mkdir(exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING', 'scope': __doc__})+'\n')
    source = ROOT/'build/md-next-levels-replay/frames.json'
    rows = json.loads(source.read_text())
    assert digest(ROOT/'Lion King, The (World).md') == 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    game = MdLab()
    trace = C.CDLL(str(ROOT/'build/md_commands.dll'))
    trace.md_commands_init.argtypes = [C.c_void_p, C.c_char_p]
    assert trace.md_commands_init(game.core._handle, str(out/'commands.csv').encode())
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1): game.core.retro_set_controller_port_device(port, 513)
    word = lambda a: struct.unpack_from('<H', bytes(game.work_ram), a)[0]
    previous = None
    losses = []
    snapshots = 0
    final = None
    try:
        for frame in range(1, 40001):
            trace.md_commands_frame(frame)
            game.step(rows[frame-1]['pad'] if frame <= 4000 else (128 if frame > 5400 else 0))
            if frame <= 4000 and frame % 100 == 1:
                snapshot = ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                if snapshot.exists():
                    assert bytes(game.work_ram) == snapshot.read_bytes()
                    snapshots += 1
            if frame >= 4000:
                lives = word(0xccee)
                if previous is not None and lives < previous:
                    losses.append({'frame': frame, 'before': previous, 'after': lives, 'health': word(0xccf6), 'level': word(0xccce)})
                    print('Original Pride lives', previous, '->', lives, 'field', frame, flush=True)
                    if lives == 0: final = frame
                previous = lives
            if final and frame == final+160:
                png(out/'game-over.png', *game.image)
                (out/'game-over-wram.bin').write_bytes(bytes(game.work_ram))
            if final and frame >= final+500: break
            game.samples.clear()
    finally:
        trace.md_commands_close()
        game.close()
    commands = list(csv.DictReader((out/'commands.csv').open()))
    music = [r for r in commands if r['selector'] == '1' and int(r['frame']) >= 4000]
    over = [r for r in music if r['caller'] == '1d692a']
    assert final and len(losses) == 9 and losses[-1]['after'] == 0, losses
    assert len(over) == 1 and int(over[0]['value']) == 327, over
    assert not any(int(r['value']) == 430 and int(r['frame']) >= final for r in music)
    report = {'result': 'PASS', 'scope': __doc__, 'ordinary_power_on': True,
              'loaded_states': False, 'life_losses': losses, 'final_life_field': final,
              'game_over_music': over, 'nonfinal_health_death_program': 430,
              'no_430_on_final_life': True, 'unchanged_prefix_wram_snapshots': snapshots,
              'source_sha256': {'input': digest(source), 'commands': digest(out/'commands.csv'),
                                'rom': digest(ROOT/'Lion King, The (World).md'),
                                'core': digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
                                'trace': digest(ROOT/'build/md_commands.dll'), 'script': digest(Path(__file__))}}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Original Pride game-over327, final-life430 exclusion PASS', flush=True)


if __name__ == '__main__': main()
