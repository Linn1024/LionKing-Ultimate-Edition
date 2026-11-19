"""Switch the independent health-death music leaf both ways through real F12.

Actual original loader restarts, profile persistence and audio-source save
fingerprints are checked; death playback itself has a separate ordinary route.
"""
import hashlib
import argparse
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32,window_for
from windows_capture import capture_client
from verify_pride_audio_state import audio_offset


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-over',action='store_true')
    over=parser.parse_args().game_over
    leaf='audio.music.pride_game_over' if over else 'audio.music.pride_health_death'
    row=436 if over else 408
    USER32.SetProcessDPIAware();out=ROOT/('build/pride-game-over-switch' if over else 'build/pride-health-death-switch');out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    command=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
             '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
             '--config',config,'--practice-level','0','--no-audio','--no-record']
    hwnd=None
    with (out/'game.log').open('wb') as f:
        process=subprocess.Popen(list(map(str,command)),cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(120):
                hwnd=window_for(process.pid)
                if hwnd:break
                assert process.poll() is None;time.sleep(.05)
            assert hwnd
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001);time.sleep(.4)
            def click(x,y):
                for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                    assert USER32.PostMessageW(hwnd,message,buttons,x|(y<<16))
                time.sleep(.4)
            def shot(name):assert capture_client(hwnd,out/(name+'.png'))==(960,672)
            time.sleep(9);key(112);shot('native-before')
            key(123);click(154,267);click(154,295);click(174,324)
            assert USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))
            assert USER32.PostMessageW(hwnd,0x20a,((-1440)&65535)<<16,300|(500<<16));time.sleep(.5)
            shot('native-tree');click(575,row);click(490,row+76);shot('staged-md');click(170,595)
            time.sleep(12)
            assert leaf+' = md' in profile.read_text()
            key(113);shot('md-restarted');key(123);shot('md-active-tree')
            click(575,row);click(490,row+53);shot('staged-native');click(170,595)
            time.sleep(12)
            assert leaf+' = snes' in profile.read_text()
            key(114);key(116);shot('native-slot-restored');key(123);shot('native-active-tree');key(123)
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0
    log=(out/'game.log').read_text(errors='replace')
    assert log.count('Loading Pridelands')==3 and 'Loaded slot 1' in log,log[-2000:]
    states=[];fingerprints=[]
    for slot in (1,2,3):
        path=out/f'tlk_slot{slot}.state';data=path.read_bytes();at=audio_offset(data)
        assert struct.unpack_from('<I',data,at+8)[0]==2
        assert struct.unpack_from('<I',data,at+112)[0]==0
        fingerprints.append(data[at+48:at+80].hex())
        states.append({'slot':slot,'frame':struct.unpack_from('<I',data,12)[0],
                       'audio_fingerprint':fingerprints[-1],'sha256':hashlib.sha256(data).hexdigest()})
    assert fingerprints[0]==fingerprints[2] and fingerprints[0]!=fingerprints[1]
    report={'result':'PASS','scope':__doc__,'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'leaf':leaf,'both_directions_persisted':True,
            'original_loader_calls':3,'native_slot_loaded_after_matching_sources':True,'states':states}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Actual F12 health-death leaf, both restarts and saved audio fingerprints PASS',flush=True)


if __name__=='__main__':main()
