"""Exercise real F12 checkpoint inheritance, live overrides and player slots."""
import hashlib
import ctypes as C
from ctypes import wintypes as W
import json
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from verify_windows import USER32, window_for, pixels
from windows_capture import capture_client
from pride_sprite_catalog import bitmap, snes_frame


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    USER32.SetProcessDPIAware()
    USER32.ClientToScreen.argtypes = [W.HWND,C.POINTER(W.POINT)]
    USER32.ClientToScreen.restype = W.BOOL
    USER32.SetCursorPos.argtypes = [C.c_int,C.c_int]
    USER32.SetCursorPos.restype = W.BOOL
    USER32.SetForegroundWindow.argtypes = [W.HWND]
    USER32.mouse_event.argtypes = [W.DWORD,W.DWORD,W.DWORD,W.DWORD,C.c_size_t]
    exe = ROOT/'engine/build-win/tlk_sdl.exe'
    identity = digest(exe)
    reference_path = ROOT/'build/pride-checkpoint-player/windows-5400/report.json'
    reference = json.loads(reference_path.read_text())
    assert reference['result'] == 'PASS' and reference['candidate_sha256'] == identity
    out = ROOT/'build/pride-checkpoint-player/switch'
    out.mkdir(exist_ok=True)
    for slot in (1,2,3,4):
        (out/f'tlk_slot{slot}.state').unlink(missing_ok=True)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 3\n')
    profile = out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    leaf = 'graphics.sprites.checkpoints'
    state = ROOT/'build/pride-checkpoint-player/windows-5400/320-both-aot/checkpoint.state'
    cmd = [exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
           '--load',state,'--resource-profile',profile,'--config',config,'--no-audio','--no-record']
    hwnd = None
    with (out/'run.log').open('wb') as log:
        process = subprocess.Popen(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline = time.monotonic()+15
            while time.monotonic() < deadline:
                hwnd = window_for(process.pid)
                if hwnd:
                    break
                assert process.poll() is None
                time.sleep(.05)
            assert hwnd
            USER32.SetForegroundWindow(hwnd)

            def key(value):
                scan = USER32.MapVirtualKeyW(value,0)
                flags = 1 | scan<<16 | (1<<24 if value in (35,36,37,38,39,40) else 0)
                assert USER32.PostMessageW(hwnd,0x100,value,flags)
                assert USER32.PostMessageW(hwnd,0x101,value,flags|0xc0000000)
                time.sleep(.35)

            def click(x,y):
                point = W.POINT(x,y)
                assert USER32.ClientToScreen(hwnd,C.byref(point))
                assert USER32.SetCursorPos(point.x,point.y)
                time.sleep(.1)
                USER32.mouse_event(0x0002,0,0,0,0)
                time.sleep(.1)
                USER32.mouse_event(0x0004,0,0,0,0)
                time.sleep(.35)

            def choose(y,source):
                click(575,y)
                capture_client(hwnd,out/f'popup-{y}-{source}-opened.png')
                click(490,y+{'inherit':31,'snes':53,'md':76}[source])
                capture_client(hwnd,out/f'selected-{y}-{source}.png')

            def top():
                # Reopening restores the table's last keyboard focus, which
                # can scroll when the child first receives a mouse click.
                click(800,300)
                point = W.POINT(800,300)
                assert USER32.ClientToScreen(hwnd,C.byref(point))
                assert USER32.SetCursorPos(point.x,point.y)
                time.sleep(.1)
                USER32.mouse_event(0x0800,0,0,1200,0)
                time.sleep(.5)

            def shot(name):
                assert capture_client(hwnd,out/(name+'.png')) == (960,672)

            def resume_save(slot,name):
                click(544,575)
                key(27)
                time.sleep(.5)
                key(111+slot)
                shot(name)

            time.sleep(1)
            key(112)
            key(123)
            top()
            click(194,323)  # Collapse Simba; checkpoint branch follows Effects.
            click(194,463)
            shot('tree')
            choose(463,'md')
            choose(519,'snes')
            shot('frames-md-palette-native-staged')
            click(170,595)
            text = profile.read_text()
            assert leaf+' = md' in text and leaf+'.palette = snes' in text and leaf+'.frames = inherit' in text
            resume_save(2,'frames-md-palette-native')
            key(123)
            top()
            shot('second-tree')
            choose(491,'snes')
            choose(519,'md')
            click(170,595)
            text = profile.read_text()
            assert leaf+'.frames = snes' in text and leaf+'.palette = md' in text
            resume_save(3,'frames-native-palette-md')
            key(123)
            top()
            shot('third-tree')
            choose(491,'inherit')
            choose(519,'inherit')
            choose(463,'snes')
            click(170,595)
            assert leaf+' = snes' in profile.read_text()
            resume_save(4,'native-branch')
        finally:
            if process.poll() is None:
                if hwnd:
                    USER32.PostMessageW(hwnd,0x10,0,0)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=10)
    assert process.returncode == 0
    assert 'Loading Pridelands' not in (out/'run.log').read_text()
    snes = (ROOT/'Lion King, The (USA).sfc').read_bytes()
    md = (ROOT/'Lion King, The (World).md').read_bytes()
    left,top,w,h,indices = bitmap(snes,snes_frame(snes,0x456de),False,with_origin=True)
    native_palette = struct.unpack_from('<16H',snes,0x7b93)
    external_palette = []
    for raw in struct.unpack_from('>16H',md,0x1d78aa):
        external_palette.append(sum((((raw>>s)&7)*4+(((raw>>s)&7)>>2))<<o for s,o in ((1,0),(5,5),(9,10))))
    for name,palette in (('frames-md-palette-native',native_palette),('frames-native-palette-md',external_palette),('native-branch',native_palette)):
        width,height,picture = pixels(out/(name+'.png'))
        assert (width,height) == (960,672)
        for y in range(h):
            for x in range(w):
                index = indices[y*w+x]
                if not index:
                    continue
                color = palette[index]
                rgb = tuple(((color>>s)&31)*8+((color>>s)&31)//4 for s in (0,5,10))
                for yy in range((112+top+y)*3,(112+top+y+1)*3):
                    for xx in range((112+left+x)*3,(112+left+x+1)*3):
                        assert picture[yy*width+xx] == rgb,(name,x,y)
    slot_frames = [struct.unpack_from('<I',(out/f'tlk_slot{n}.state').read_bytes(),12)[0] for n in (1,2,3,4)]
    assert all(a < b for a,b in zip(slot_frames,slot_frames[1:]))
    assert digest(exe) == identity
    report = dict(result='PASS',scope=__doc__,candidate_sha256=identity,slot_frames=slot_frames,
        actual_F12_inheritance_and_live_overrides=True,level_not_restarted=True,
        original_head_pixels_verified=3*657*9,reference_sha256=digest(reference_path),
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        artifacts_sha256={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Actual F12 checkpoint branch/leaf overrides, original source pixels and uninterrupted slots PASS',flush=True)


if __name__ == '__main__':
    main()
