"""Operate the actual F12 hyena-taunt choice and confirm current-level restarts."""
import json
import argparse
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cue',choices=('hyena_taunt','defeat_puff','lizard_defeat'),default='hyena_taunt')
    cue=parser.parse_args().cue
    if cue=='lizard_defeat':cue='defeat_puff'  # Earlier research-tool spelling.
    leaf='audio.effects.world.'+cue
    row_y=436 if cue=='hyena_taunt' else 464
    USER32.SetProcessDPIAware()
    out=ROOT/('build/pride-hyena-taunt-switch' if cue=='hyena_taunt' else 'build/pride-lizard-defeat-switch');out.mkdir(parents=True,exist_ok=True)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
             '--config',str(config),'--practice-level','0','--no-audio','--no-record']
    with (out/'game.log').open('wb') as log:
        process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd=None
        try:
            for _ in range(100):
                hwnd=window_for(process.pid)
                if hwnd:break
                time.sleep(.05)
            assert hwnd
            def key(value):
                USER32.PostMessageW(hwnd,0x100,value,1);USER32.PostMessageW(hwnd,0x101,value,0xc0000001);time.sleep(.35)
            def click(x,y):
                for msg,buttons in ((0x200,0),(0x201,1),(0x202,0)):assert USER32.PostMessageW(hwnd,msg,buttons,x|(y<<16))
                time.sleep(.35)
            def shot(name):assert capture_client(hwnd,out/(name+'.png'))==(960,672)
            time.sleep(9)
            # Include the extended physical right-arrow scan code; hotkeys
            # use key symbols, but held gameplay input uses SDL scan codes.
            USER32.PostMessageW(hwnd,0x100,0x27,0x014d0001);time.sleep(.4)
            USER32.PostMessageW(hwnd,0x101,0x27,0xc14d0001)
            key(112)
            key(123);click(154,267);click(154,295);click(174,351);click(194,407)
            USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))
            USER32.PostMessageW(hwnd,0x20a,((-1440)&65535)<<16,300|(500<<16));time.sleep(.5)
            shot('tree')
            click(575,row_y);click(490,row_y+76);shot('md-staged');click(170,595);time.sleep(15)
            assert leaf+' = md' in profile.read_text()
            key(113);key(123);shot('md-active')
            click(575,row_y);click(490,row_y+53);shot('native-staged');click(170,595);time.sleep(15)
            assert leaf+' = snes' in profile.read_text()
            key(114);key(123);shot('native-active');key(123)
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0
    assert (out/'game.log').read_text().count('Loading Pridelands')>=3
    positions=[]
    for slot in (1,2,3):
        state=out/f'tlk_slot{slot}.state';frame=struct.unpack_from('<I',state.read_bytes(),12)[0]+1
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(out))
        with (out/f'slot{slot}.log').open('wb') as log:
            subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                            '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                            '--load',str(state),'--frames',str(frame)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        ram=(out/f'hl_wram_{frame}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
        assert word(0x1ff9e)==0 and word(0xdf) in (0x387,0x80d)
        positions.append([word(0xb21b),word(0xb21d)])
    assert positions[0]!=positions[1] and positions[1]==positions[2],positions
    (out/'report.json').write_text(json.dumps({'result':'PASS','source_id':leaf,'source_persisted_both_directions':True,
        'original_current_level_loader_calls':3,'all_slots_remain_pride':True,'positions':positions},indent=2)+'\n')
    print('Actual F12',cue,'switching persists and restarts Pride both ways PASS',flush=True)


if __name__=='__main__':main()
