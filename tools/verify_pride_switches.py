"""Use actual F12 controls to switch pickup sources, restart and load slots.

All profiles/saves/captures belong to this test's own ignored folder. Mouse and
key events go only to the child SDL window; desktop focus/cursor stay untouched.
"""
import csv
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
    out=ROOT/'build/pride-layout-switch-verified';out.mkdir(parents=True,exist_ok=True)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    (out/'host.ini').write_text('opengl = 1\nscale = 3\n')
    env=os.environ.copy();env['TLK_LAYOUT_TRACE']=str(out/'moves.csv')
    command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
             '--config',str(out/'host.ini'),'--practice-level','0','--no-audio','--no-record']
    with (out/'game.log').open('wb') as log:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd=None
        try:
            for _ in range(100):
                hwnd=window_for(process.pid)
                if hwnd:break
                time.sleep(.05)
            assert hwnd,'Child SDL window not found'
            def key(v):
                assert USER32.PostMessageW(hwnd,0x100,v,1)
                assert USER32.PostMessageW(hwnd,0x101,v,0xc0000001)
                time.sleep(.35)
            def click(x,y):
                position=x|(y<<16)
                for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                    assert USER32.PostMessageW(hwnd,message,buttons,position)
                time.sleep(.35)
            def shot(name):
                assert capture_client(hwnd,out/(name+'.png'))==(960,672),'Unexpected client size'
            def save(slot,source):
                path=out/f'tlk_slot{slot}.state'
                for _ in range(10):
                    key(111+slot)
                    raw=path.read_bytes();version=struct.unpack_from('<I',raw,8)[0]
                    flags=struct.unpack_from('<I',raw,32)[0] if version>=2 else 0
                    if flags&0x80000000:
                        assert flags&3==source,'Saved gameplay source differs'
                        return path
                    time.sleep(1)
                raise AssertionError('Restart did not reach actual Pride Lands')
            def choose(md):
                key(123);click(584,492);click(490,568 if md else 546);shot('md-staged' if md else 'snes-staged')
                click(170,595)
                time.sleep(15)
                assert 'gameplay.levels.pride_lands.pickups = '+('md' if md else 'snes') in profile.read_text()
            time.sleep(9);key(123);shot('initial')
            click(154,267);click(154,324);click(174,436);click(194,464)
            # The menu is already open for the first source edit.
            click(584,492);click(490,568);shot('md-staged');click(170,595);time.sleep(15)
            save(2,2);shot('md-restarted');print('F12 pickup SNES -> MD restart PASS',flush=True)
            choose(False);native=save(1,0);shot('snes-restarted')
            before=hashlib.sha256(native.read_bytes()).hexdigest()
            print('F12 pickup MD -> SNES restart PASS',flush=True)
            choose(True);save(2,2);key(116);shot('state-source-rejected')
            assert hashlib.sha256(native.read_bytes()).hexdigest()==before,'Rejected slot changed'
            choose(False);key(116);shot('matching-state-loaded')
            assert hashlib.sha256(native.read_bytes()).hexdigest()==before
            print('F5 mismatched rejection and matching load PASS',flush=True)
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0,'SDL exited with an error'
    text=(out/'game.log').read_text(errors='replace')
    assert 'Slot 1: State pickup source differs; match it in F12' in text
    assert 'Loaded slot 1' in text
    with (out/'moves.csv').open() as stream:moves=list(csv.DictReader(stream))
    expected=[{'marker':'41','native_x':'560','native_y':'208','md_x':'560','md_y':'224'},
              {'marker':'18','native_x':'320','native_y':'496','md_x':'336','md_y':'496'}]
    assert moves==expected*2,'Relocations did not follow the two MD restarts exclusively'
    report={'result':'PASS','scope':__doc__,'md_restarts':2,'snes_restarts':2,
            'matching_slot_load':True,'mismatched_slot_rejected':True,'saved_slot_unchanged':True,'moves':moves}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
