"""Exercise both F12 directions for Pride Rock music in the actual player."""
import csv
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32, window_for
from windows_capture import capture_client


def main():
    USER32.SetProcessDPIAware()
    out = ROOT/'build/final-music-switch'
    out.mkdir(exist_ok=True)
    profile = out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 3\n')
    env = os.environ.copy()
    env['TLK_MD_SOUND_COMMANDS'] = str(out/'commands.csv')
    command = [str(ROOT/'dist/LionKing.exe'), '--rom', str(ROOT/'Lion King, The (USA).sfc'),
               '--md-rom', str(ROOT/'Lion King, The (World).md'), '--config', str(config),
               '--resource-profile', str(profile), '--practice-level', '9',
               '--no-audio', '--no-record', '--wav', str(out/'start.wav'), '--wav-seconds', '1']
    with (out/'game.log').open('wb') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                   stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd = None
        try:
            for _ in range(100):
                hwnd = window_for(process.pid)
                if hwnd:
                    break
                time.sleep(.1)
            assert hwnd

            def key(value):
                assert USER32.PostMessageW(hwnd, 0x100, value, 1)
                assert USER32.PostMessageW(hwnd, 0x101, value, 0xc0000001)
                time.sleep(.4)

            def click(x, y):
                for message, buttons in ((0x200, 0), (0x201, 1), (0x202, 0)):
                    assert USER32.PostMessageW(hwnd, message, buttons, x | (y << 16))
                time.sleep(.4)

            def shot(name):
                assert capture_client(hwnd, out/(name+'.png')) == (960, 672)

            time.sleep(10)
            key(112)
            shot('before')
            key(123)
            click(154, 267)  # Collapse Graphics.
            click(154, 295)  # Open Audio.
            click(174, 324)  # Open Music.
            USER32.PostMessageW(hwnd, 0x200, 0, 300 | (500 << 16))
            USER32.PostMessageW(hwnd, 0x20a, ((-1440) & 65535) << 16, 300 | (500 << 16))
            time.sleep(.6)
            shot('native-tree')
            click(575, 380)
            click(490, 456)
            shot('staged-md')
            click(170, 595)
            time.sleep(12)
            assert 'audio.music.pride_rock = md' in profile.read_text()
            key(113)
            shot('restarted-md')
            key(123)
            shot('active-md-tree')
            click(575, 380)
            click(490, 433)
            shot('staged-native')
            click(170, 595)
            time.sleep(12)
            assert 'audio.music.pride_rock = snes' in profile.read_text()
            key(114)
            shot('restarted-native')
            key(123)
            shot('active-native-tree')
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
    states = []
    for slot in (1, 2, 3):
        state = out/f'tlk_slot{slot}.state'
        frame = struct.unpack_from('<I', state.read_bytes(), 12)[0]+1
        env = os.environ.copy()
        env.update(TLK_WRAM_DUMP=str(frame), TLK_WRAM_DIR=str(out))
        command = [str(ROOT/'engine/build-win/tlk_headless.exe'), '--rom',
                   str(ROOT/'Lion King, The (USA).sfc'), '--md-rom',
                   str(ROOT/'Lion King, The (World).md'), '--resource-profile', str(profile),
                   '--load', str(state), '--frames', str(frame)]
        with (out/f'slot{slot}.log').open('wb') as log:
            subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=120)
        ram = (out/f'hl_wram_{frame}.bin').read_bytes()
        word = lambda at: struct.unpack_from('<H', ram, at)[0]
        assert word(0x1ff9e) == 9 and word(0xdf) == 0x549
        states.append({'level': word(0x1ff9e), 'descriptor': word(0xdf),
                       'x': word(0xb21b), 'y': word(0xb21d)})
    tracks = [int(r['value']) for r in csv.DictReader((out/'commands.csv').open())
              if r['selector'] == '1']
    assert 432 in tracks
    # A restart must execute the original loader again in each direction.
    assert (out/'game.log').read_text().count('Loading Pride Rock') >= 3
    report = {'result': 'PASS', 'actual_f12_both_directions': True,
              'same_level_after_each_restart': states, 'original_md_program': 432}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Actual Pride Rock F12 music switching and original level restarts PASS', flush=True)


if __name__ == '__main__':
    main()
