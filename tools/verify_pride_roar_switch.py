"""Use the actual F12 tree to restart with roar behavior and guard saved slots."""
import hashlib
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
    out = ROOT / 'build/pride-roar-switch'
    out.mkdir(parents=True, exist_ok=True)
    profile = out / 'resources.ini'; profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config = out / 'host.ini'; config.write_text('opengl = 1\nscale = 3\n')
    env = os.environ.copy(); env['TLK_ROAR_TRACE'] = str(out / 'roar.csv')
    command = [str(ROOT / 'dist/LionKing.exe'), '--rom', str(ROOT / 'Lion King, The (USA).sfc'),
               '--md-rom', str(ROOT / 'Lion King, The (World).md'), '--config', str(config),
               '--resource-profile', str(profile), '--practice-level', '0', '--no-audio', '--no-record']
    with (out / 'game.log').open('wb') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd = None
        try:
            for _ in range(100):
                hwnd = window_for(process.pid)
                if hwnd: break
                time.sleep(.05)
            assert hwnd
            def key(value):
                assert USER32.PostMessageW(hwnd, 0x100, value, 1)
                assert USER32.PostMessageW(hwnd, 0x101, value, 0xc0000001)
                time.sleep(.35)
            def click(x, y):
                for message, buttons in ((0x200, 0), (0x201, 1), (0x202, 0)):
                    assert USER32.PostMessageW(hwnd, message, buttons, x | (y << 16))
                time.sleep(.35)
            def shot(name):
                assert capture_client(hwnd, out / (name + '.png')) == (960, 672)
            def save(slot, md):
                key(111 + slot)
                path = out / f'tlk_slot{slot}.state'
                raw = path.read_bytes(); flags = struct.unpack_from('<I', raw, 32)[0]
                assert flags & 0x80000000 and bool(flags & 16) == md, (slot, flags)
                return path
            def choose(md, first=False):
                key(123)
                if first:
                    click(154, 267); click(154, 324); click(174, 351)
                shot('tree-' + ('md' if md else 'snes'))
                click(584, 436)
                click(490, 512 if md else 489)
                shot('staged-' + ('md' if md else 'snes'))
                click(170, 595); time.sleep(15)
                assert 'gameplay.simba.roar = ' + ('md' if md else 'snes') in profile.read_text()
            time.sleep(9)
            native = save(1, False); before = hashlib.sha256(native.read_bytes()).hexdigest()
            choose(True, True)
            USER32.PostMessageW(hwnd, 0x100, 65, 1); time.sleep(.4)
            USER32.PostMessageW(hwnd, 0x101, 65, 0xc0000001); time.sleep(1)
            save(2, True); shot('md-restarted')
            key(116); shot('mismatched-slot-rejected')
            assert hashlib.sha256(native.read_bytes()).hexdigest() == before
            choose(False); key(116); shot('matching-slot-loaded')
            assert hashlib.sha256(native.read_bytes()).hexdigest() == before
        finally:
            if process.poll() is None:
                if hwnd: USER32.PostMessageW(hwnd, 0x10, 0, 0)
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.terminate(); process.wait(timeout=10)
    assert process.returncode == 0
    text = (out / 'game.log').read_text(errors='replace')
    assert 'State roar behavior differs; match it in F12' in text
    assert 'Loaded slot 1' in text
    assert (out / 'roar.csv').stat().st_size > 100
    (out / 'report.json').write_text(json.dumps({'result': 'PASS', 'source_restarts_both_directions': True,
        'mismatched_slot_rejected': True, 'matching_slot_loaded': True, 'saved_slot_unchanged': True}, indent=2) + '\n')
    print('Actual F12 roar switching, current-level restarts and source-aware slots PASS', flush=True)


if __name__ == '__main__':
    main()
