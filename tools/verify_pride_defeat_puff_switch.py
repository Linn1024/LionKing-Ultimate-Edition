"""Exercise actual F12 puff branch inheritance and independent live overrides."""
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
    out = ROOT/'build/pride-defeat-puff-switch'
    out.mkdir(parents=True, exist_ok=True)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 3\n')
    profile = out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    leaf = 'graphics.sprites.effects.defeat_puff'
    command = [ROOT/'dist/LionKing.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
               '--md-rom', ROOT/'Lion King, The (World).md', '--load',
               ROOT/'build/pride-defeat-puff-art/ready.state', '--resource-profile', profile,
               '--config', config, '--no-audio', '--no-record']
    hwnd = None
    with (out/'game.log').open('wb') as log:
        process = subprocess.Popen(list(map(str, command)), cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
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
                time.sleep(.35)
            def click(x, y):
                for message, buttons in ((0x200, 0), (0x201, 1), (0x202, 0)):
                    assert USER32.PostMessageW(hwnd, message, buttons, x | y << 16)
                time.sleep(.35)
            def choose(y, option):
                click(575, y)
                click(490, y+{'inherit': 31, 'snes': 53, 'md': 76}[option])
            def shot(name):
                assert capture_client(hwnd, out/(name+'.png')) == (960, 672)
            def resume_and_save(slot):
                click(544, 575)
                key(9)
                time.sleep(.5)
                key(111+slot)
            time.sleep(1)
            key(112)
            key(123)
            click(194, 323)  # Collapse Simba, exposing the new sibling Effects.
            click(194, 435)
            click(214, 463)
            shot('tree')
            choose(463, 'md')
            choose(519, 'snes')
            shot('branch-md-palette-native-staged')
            click(170, 595)
            text = profile.read_text()
            assert leaf+' = md' in text and leaf+'.frames = inherit' in text and leaf+'.palette = snes' in text
            shot('frames-md-palette-native-active')
            resume_and_save(2)
            key(123)
            choose(491, 'snes')
            choose(519, 'md')
            click(170, 595)
            text = profile.read_text()
            assert leaf+'.frames = snes' in text and leaf+'.palette = md' in text
            shot('frames-native-palette-md-active')
            resume_and_save(3)
            key(123)
            choose(491, 'inherit')
            choose(519, 'inherit')
            choose(463, 'snes')
            click(170, 595)
            text = profile.read_text()
            assert leaf+' = snes' in text and leaf+'.frames = inherit' in text and leaf+'.palette = inherit' in text
            shot('native-branch-active')
            resume_and_save(4)
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
    assert 'Loading Pridelands' not in (out/'game.log').read_text(), 'Graphics change restarted the level'
    frames = []
    for slot in (1, 2, 3, 4):
        state = out/f'tlk_slot{slot}.state'
        frame = struct.unpack_from('<I', state.read_bytes(), 12)[0]
        frames.append(frame)
        env = os.environ.copy()
        env.update(TLK_WRAM_DUMP=str(frame+1), TLK_WRAM_DIR=str(out))
        with (out/f'slot{slot}.log').open('wb') as log:
            subprocess.run(list(map(str, [ROOT/'engine/build-win/tlk_headless.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
                                         '--md-rom', ROOT/'Lion King, The (World).md', '--resource-profile', profile,
                                         '--load', state, '--frames', frame+1])), cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=120)
        ram = (out/f'hl_wram_{frame+1}.bin').read_bytes()
        assert struct.unpack_from('<H', ram, 0x1ff9e)[0] == 0 and struct.unpack_from('<H', ram, 0xdf)[0] in (0x387, 0x80d)
    assert all(a < b for a, b in zip(frames, frames[1:]))
    report = {'result': 'PASS', 'scope': __doc__, 'source_id': leaf,
              'branch_inheritance_and_both_leaf_overrides_persisted': True,
              'graphics_changes_invoke_no_level_loader': True, 'slot_frames': frames,
              'all_slots_remain_actual_pride': True}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Actual F12 defeat-puff branch/leaf overrides, live apply and Pride slots PASS', flush=True)


if __name__ == '__main__':
    main()
