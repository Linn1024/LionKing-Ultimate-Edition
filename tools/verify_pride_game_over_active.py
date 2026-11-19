"""Capture real F12 availability while the selected game-over theme is active.

This is a loaded-state UI check, separate from ordinary game-over playback.
Inspect active-tree.png: the selected leaf must report Mega Drive as active.
"""
import hashlib
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32, window_for
from windows_capture import capture_client
from verify_pride_audio_state import audio_offset


def main():
    USER32.SetProcessDPIAware()
    source = ROOT/'build/pride-game-over-music/hard-over-playing.state'
    out = ROOT/'build/pride-game-over-active';out.mkdir(exist_ok=True)
    profile = out/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.music.pride_game_over = md\n')
    config = out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    command = [ROOT/'dist/LionKing.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
               '--md-rom', ROOT/'Lion King, The (World).md', '--resource-profile', profile,
               '--config', config, '--load', source, '--no-audio', '--no-record',
               '--wav', out/'live.wav', '--wav-seconds', '10']
    hwnd = None
    with (out/'game.log').open('wb') as log:
        process = subprocess.Popen(list(map(str, command)), cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(120):
                hwnd = window_for(process.pid)
                if hwnd: break
                assert process.poll() is None
                time.sleep(.05)
            assert hwnd
            time.sleep(.5)
            def key(value):
                assert USER32.PostMessageW(hwnd, 0x100, value, 1)
                assert USER32.PostMessageW(hwnd, 0x101, value, 0xc0000001)
                time.sleep(.3)
            key(112)
            size = capture_client(hwnd, out/'playing.png')
            assert size == (768, 672), size
            key(123)
            # The same fixed-width resource dialog is centered in this native
            # 768px window rather than the 960px practice-stage switch test.
            dx = -96
            def click(x, y):
                for message, buttons in ((0x200, 0), (0x201, 1), (0x202, 0)):
                    assert USER32.PostMessageW(hwnd, message, buttons, (x+dx)|(y<<16))
                time.sleep(.3)
            click(154, 267);click(154, 295);click(174, 324)
            assert USER32.PostMessageW(hwnd, 0x200, 0, (300+dx)|(500<<16))
            assert USER32.PostMessageW(hwnd, 0x20a, ((-1440)&65535)<<16, (300+dx)|(500<<16))
            time.sleep(.4)
            assert capture_client(hwnd, out/'active-tree.png') == size
        finally:
            if process.poll() is None:
                if hwnd: USER32.PostMessageW(hwnd, 0x10, 0, 0)
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.terminate();process.wait(timeout=10)
    assert process.returncode == 0
    state = (out/'tlk_slot1.state').read_bytes();at = audio_offset(state)
    assert struct.unpack_from('<I', state, at+20)[0] == 327
    report = {'result': 'PASS', 'scope': __doc__,
              'player_sha256': hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
              'loaded_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'saved_frame': struct.unpack_from('<I', state, 12)[0], 'saved_track': 327,
              'menu_captured': True, 'pixel_size': list(size),
              'active_tree_sha256': hashlib.sha256((out/'active-tree.png').read_bytes()).hexdigest()}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Actual playing327 and game-over F12 menu captured; inspect active-tree.png', flush=True)


if __name__ == '__main__': main()
