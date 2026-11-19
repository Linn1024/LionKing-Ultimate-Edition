"""Verify actual off-Pride checkpoint rows report the native fallback."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

from audit_scenes import ROOT
from verify_windows import USER32, window_for, pixels, hashes
from windows_capture import capture_client


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    USER32.SetProcessDPIAware()
    out = ROOT/'build/pride-checkpoint-player/fallback-ui'
    out.mkdir(exist_ok=True)
    new = ROOT/'engine/build-win/tlk_sdl.exe'
    old = ROOT/'engine/build-win/tlk_checkpoint_ui_before.exe'
    old_cpp = ROOT/'build/pride-checkpoint-player/tlk_menu_imgui-before-scope.cpp'
    cpp = ROOT/'engine/runner/tlk_menu_imgui.cpp'
    addition = '        !strncmp(node->id,"graphics.sprites.checkpoints.",29) ||\n'
    assert cpp.read_text().replace(addition,'') == old_cpp.read_text()
    assert digest(old) == '28e504f406e819b1d5dedbc8e5ac6bf370131428f45e84906d34d74a75c62a0f'
    identity = digest(new)
    for label,exe in (('before',old),('after',new)):
        folder = out/label
        folder.mkdir(exist_ok=True)
        config = folder/'host.ini'
        config.write_text('opengl = 1\nscale = 3\n')
        profile = folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.sprites.checkpoints = md\n')
        command = [exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                   '--resource-profile',profile,'--config',config,'--practice-level','1','--menu-at','2300',
                   '--menu-page','resources','--no-pace','--no-audio','--no-record','--dump-scene',folder/'scene.json']
        hwnd = None
        with (folder/'run.log').open('wb') as log:
            process = subprocess.Popen(list(map(str,command)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                deadline = time.monotonic()+15
                while time.monotonic() < deadline:
                    hwnd = window_for(process.pid)
                    if hwnd:
                        break
                    assert process.poll() is None
                    time.sleep(.05)
                assert hwnd
                time.sleep(15)
                for x,y in ((194,323),(194,463)):
                    for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                        assert USER32.PostMessageW(hwnd,message,buttons,x|y<<16)
                    time.sleep(.35)
                assert capture_client(hwnd,folder/'tree.png') == (960,672)
            finally:
                if process.poll() is None:
                    if hwnd:
                        USER32.PostMessageW(hwnd,0x10,0,0)
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.terminate();process.wait(timeout=10)
        assert process.returncode == 0
        scene = json.loads((folder/'scene.json').read_text())
        assert scene['level'] == 1 and scene['checkpoint_adapter']['pixels'] == 0
        assert 'frames=2300 ' in (folder/'run.log').read_text()
    assert hashes(out/'before/run.log') == hashes(out/'after/run.log')
    width,height,before = pixels(out/'before/tree.png')
    w,h,after = pixels(out/'after/tree.png')
    assert (width,height) == (w,h) == (960,672)
    changes = [(i%w,i//w) for i,(a,b) in enumerate(zip(before,after)) if a != b]
    assert changes and all(590 <= x < 704 and 480 <= y < 535 for x,y in changes),changes[:20]
    assert any(y < 508 for x,y in changes) and any(y >= 508 for x,y in changes)
    assert digest(new) == identity
    report = dict(result='PASS',scope=__doc__,candidate_sha256=identity,baseline_sha256=digest(old),
        label_changed_pixels=len(changes),only_checkpoint_active_labels_changed=True,
        diagnostic_practice_scene_only=True,guest_hashes_exact=True,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),cpp,old_cpp)},
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Actual off-Pride checkpoint fallback labels changed only; guest and remaining UI pixels exact PASS',flush=True)


if __name__ == '__main__':
    main()
