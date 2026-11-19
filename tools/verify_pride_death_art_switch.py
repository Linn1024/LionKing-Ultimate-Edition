"""Exercise real F12 cub frame/palette changes during a loaded death animation."""
import hashlib
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    USER32.SetProcessDPIAware()
    out=ROOT/'build/pride-death-art-switch';out.mkdir(exist_ok=True)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(out/'coverage.json')
    cmd=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
         '--md-rom',ROOT/'Lion King, The (World).md','--load',ROOT/'build/pride-death-art/playing.state',
         '--resource-profile',profile,'--config',config,'--no-audio','--no-record']
    hwnd=None
    with (out/'game.log').open('wb') as log:
        process=subprocess.Popen(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(150):
                hwnd=window_for(process.pid)
                if hwnd:break
                assert process.poll() is None
                time.sleep(.05)
            assert hwnd
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001)
                time.sleep(.18)
            def click(x,y):
                for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                    assert USER32.PostMessageW(hwnd,message,buttons,x|y<<16)
                time.sleep(.18)
            def shot(name):assert capture_client(hwnd,out/(name+'.png'))==(960,672)
            key(112);key(123);shot('native-tree')
            for name,row in (('frames',379),('palette',408)):
                click(575,row);click(490,row+76);click(170,595)
                assert f'graphics.sprites.simba.cub.{name} = md' in profile.read_text()
                shot('md-'+name+'-tree')
            click(544,575);key(9);key(116);key(113);key(123);shot('md-active-tree')
            for name,row in (('frames',379),('palette',408)):
                click(575,row);click(490,row+53);click(170,595)
                assert f'graphics.sprites.simba.cub.{name} = snes' in profile.read_text()
            shot('native-active-tree');click(544,575);key(9);key(116);key(114)
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0
    text=(out/'game.log').read_text()
    assert 'Loading Pridelands' not in text and text.count('Loaded slot 1')==2,text[-3000:]
    frames=[struct.unpack_from('<I',(out/f'tlk_slot{i}.state').read_bytes(),12)[0] for i in (1,2,3)]
    assert all(4550<=f<4774 for f in frames),frames
    coverage=json.loads((out/'coverage.json').read_text())
    assert any(0x4c65d<=r['snes']<=0x4ca98 for r in coverage['seen_cub_poses']),coverage
    report={'result':'PASS','scope':__doc__,'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'both_sources_both_directions':True,'original_loader_restarted':False,'slot_frames':frames,
            'matching_graphics_compatible_slot_restored_twice':True,'coverage':coverage}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Actual death F12 frames/palette both directions, no restart, compatible slots PASS',flush=True)


if __name__=='__main__':main()
