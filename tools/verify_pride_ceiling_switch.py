"""Operate both ceiling leaves in the actual F12 tree and test saved slots."""
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
    USER32.SetProcessDPIAware();out=ROOT/'build/pride-ceiling-switch';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    command=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--config',config,'--practice-level','0','--no-audio','--no-record']
    hwnd=None;slots=[]
    with (out/'game.log').open('wb') as log:
        process=subprocess.Popen(list(map(str,command)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(150):
                hwnd=window_for(process.pid)
                if hwnd:break
                assert process.poll() is None;time.sleep(.05)
            assert hwnd
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001);time.sleep(.35)
            def click(x,y):
                for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                    assert USER32.PostMessageW(hwnd,message,buttons,x|(y<<16))
                time.sleep(.35)
            def shot(name):assert capture_client(hwnd,out/(name+'.png'))==(960,672)
            def save(slot,mask):
                key(111+slot);data=(out/f'tlk_slot{slot}.state').read_bytes()
                flags=struct.unpack_from('<I',data,32)[0]
                assert flags&0x80000000 and flags&0x0c000000==mask,(slot,hex(flags),hex(mask))
                slots.append({'slot':slot,'ceiling_flags':mask,'frame':struct.unpack_from('<I',data,12)[0]})
                return hashlib.sha256(data).hexdigest()
            def choose(which,md,first=False):
                key(123)
                if first:
                    click(154,267);click(154,324);click(174,436);click(194,464)
                    assert USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))
                    assert USER32.PostMessageW(hwnd,0x20a,((-2400)&65535)<<16,300|(500<<16))
                    time.sleep(.5)
                    shot('pride-expanded')
                    click(214,378)
                    assert USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))
                    time.sleep(.35)
                    assert USER32.PostMessageW(hwnd,0x20a,((-2400)&65535)<<16,300|(500<<16))
                    time.sleep(.5)
                shot('tree-'+which+str(md))
                row=406 if which=='rows' else 434
                click(584,row);click(490,row+(76 if md else 53))
                shot('staged-'+which+str(md));click(170,595);time.sleep(15)
                assert 'gameplay.levels.pride_lands.ceiling_'+which+' = '+('md' if md else 'snes') in profile.read_text()
            time.sleep(9);original=save(1,0)
            choose('rows',True,True);save(2,0x04000000);shot('rows-only')
            key(116);shot('native-slot-rejected-rows')
            choose('clearance',True);save(3,0x0c000000);shot('both')
            choose('rows',False);save(2,0x08000000);shot('clearance-only')
            key(116);shot('native-slot-rejected-clearance')
            choose('clearance',False);key(116);shot('native-restored')
            assert hashlib.sha256((out/'tlk_slot1.state').read_bytes()).hexdigest()==original
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0
    text=(out/'game.log').read_text(errors='replace')
    assert 'State ceiling row source differs' in text and 'State ceiling clearance source differs' in text
    assert 'Loaded slot 1' in text and text.count('Loading Pridelands')==5,text[-2000:]
    report={'result':'PASS','scope':__doc__,'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
        'independent_leaf_flags':slots,'source_restarts_both_directions':True,
        'both_mismatch_reasons_observed':True,'native_saved_slot_unchanged':True}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Actual F12 ceiling choices: both leaves, independent flags/restarts, rejected and matching slots PASS',flush=True)


if __name__=='__main__':main()
