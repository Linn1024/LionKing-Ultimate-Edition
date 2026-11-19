"""Drive the actual F12 cub-frame choice in the selected cub scenes without a restart."""
import argparse
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32, window_for
from windows_capture import capture_client


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exile', action='store_true')
    exile = parser.parse_args().exile
    USER32.SetProcessDPIAware()
    out = ROOT/('build/exile-cub-switch' if exile else 'build/next-cub-switch')
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for level in ((4,) if exile else (1, 2)):
        folder = out/str(level)
        folder.mkdir(exist_ok=True)
        config = folder/'host.ini'
        config.write_text('opengl = 1\nscale = 3\n')
        profile = folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
        env = os.environ.copy()
        env['TLK_SPRITE_REPORT'] = str(folder/'coverage.json')
        command = [ROOT/'dist/LionKing.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
                   '--md-rom', ROOT/'Lion King, The (World).md', '--load',
                   ROOT/f'build/{"exile-cub-art" if exile else "next-cub-art"}/{level}-start.state', '--resource-profile', profile,
                   '--config', config, '--no-audio', '--no-record']
        hwnd = None
        with (folder/'game.log').open('wb') as log:
            process = subprocess.Popen(list(map(str, command)), cwd=ROOT, env=env,
                                       stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                for _ in range(150):
                    hwnd = window_for(process.pid)
                    if hwnd:
                        break
                    assert process.poll() is None
                    time.sleep(.05)
                assert hwnd
                def key(value):
                    assert USER32.PostMessageW(hwnd, 0x100, value, 1)
                    assert USER32.PostMessageW(hwnd, 0x101, value, 0xc0000001)
                    time.sleep(.4)
                def click(x, y):
                    for message, buttons in ((0x200, 0), (0x201, 1), (0x202, 0)):
                        assert USER32.PostMessageW(hwnd, message, buttons, x | y << 16)
                    time.sleep(.4)
                def shot(name):
                    assert capture_client(hwnd, folder/(name+'.png')) == (960, 672)
                time.sleep(1)
                key(112)
                key(123)
                shot('tree')
                click(575, 379)
                click(490, 455)
                shot('md-staged')
                click(170, 595)
                assert 'graphics.sprites.simba.cub.frames = md' in profile.read_text()
                shot('md-active')
                click(544, 575)
                key(9)  # Close returns to Settings; Tab resumes the game.
                time.sleep(1)
                key(113)
                key(123)
                shot('md-active-tree')
                click(575, 379)
                click(490, 432)
                click(170, 595)
                assert 'graphics.sprites.simba.cub.frames = snes' in profile.read_text()
                shot('native-active-tree')
                click(544, 575)
                key(9)
                key(114)
            finally:
                if process.poll() is None:
                    if hwnd:
                        USER32.PostMessageW(hwnd, 0x10, 0, 0)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        process.wait(timeout=10)
        assert process.returncode == 0
        text = (folder/'game.log').read_text()
        assert not any('Loading '+name in text for name in ('Monkeys', 'Graveyard', 'Exile')), 'Live artwork apply restarted a level'
        frames = [struct.unpack_from('<I', (folder/f'tlk_slot{i}.state').read_bytes(), 12)[0] for i in (1, 2, 3)]
        assert frames[0] < frames[1] < frames[2]
        coverage = json.loads((folder/'coverage.json').read_text())
        assert coverage['seen_by_role']['cub'] > 0
        results[str(level)] = {'persisted_both_directions': True, 'original_loader_restarted': False,
                               'slot_frames': frames, 'coverage': coverage}
        print('Actual F12 cub frames: level', level, 'both directions, no restart PASS', flush=True)
    (out/'report.json').write_text(json.dumps({'result': 'PASS', 'scope': __doc__, 'levels': results}, indent=2)+'\n')


if __name__ == '__main__':
    main()
