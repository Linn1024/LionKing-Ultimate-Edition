"""Drive F12 music switching and verify the restart stays in the later level."""
import argparse,csv,json,os,struct,subprocess,time
from audit_scenes import ROOT
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--level',type=int,choices=(2,3),default=2)
    level=parser.parse_args().level
    leaf,track,name,descriptor=('elephant_graveyard',83,'Graveyard',0x3eb) if level==2 else ('stampede',145,'Stampede',0x41d)
    USER32.SetProcessDPIAware();out=ROOT/('build/next-music-switch' if level==2 else 'build/stampede-music-switch');out.mkdir(parents=True,exist_ok=True)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngameplay.levels.pride_lands.contacts = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(out/'commands.csv')
    cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),'--config',str(config),'--practice-level',str(level),'--no-audio','--no-record','--wav',str(out/'start.wav'),'--wav-seconds','1']
    with (out/'game.log').open('wb') as f:
        process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd=None
        try:
            for _ in range(100):
                hwnd=window_for(process.pid)
                if hwnd:break
                time.sleep(.05)
            assert hwnd
            def key(v):
                assert USER32.PostMessageW(hwnd,0x100,v,1);assert USER32.PostMessageW(hwnd,0x101,v,0xc0000001);time.sleep(.35)
            def click(x,y):
                for message,buttons in ((0x200,0),(0x201,1),(0x202,0)):assert USER32.PostMessageW(hwnd,message,buttons,x|(y<<16))
                time.sleep(.35)
            def shot(name):
                size=capture_client(hwnd,out/(name+'.png'))
                assert (size in ((960,672),(768,672)) if level==3 else size==(960,672)),size
            time.sleep(9)
            USER32.PostMessageW(hwnd,0x100,0x27,1);time.sleep(.8);USER32.PostMessageW(hwnd,0x101,0x27,0xc0000001);time.sleep(.4)
            key(112);shot('before')
            key(123);click(154,267);click(154,295);click(174,324);shot('music-tree')
            click(575,436 if level==2 else 464);click(490,512 if level==2 else 540);shot('staged');click(170,595)
            time.sleep(15)
            assert 'audio.music.'+leaf+' = md' in profile.read_text(),'F12 music selection failed'
            key(113);shot('restarted')
            key(123);shot('active-music-tree')
            if level==3:
                # Stampede returns to 768 client pixels after closing F12;
                # the same 736-pixel panel is now centered 96 pixels left.
                click(479,464);click(394,517);shot('staged-native');click(74,595)
                time.sleep(15)
                assert 'audio.music.stampede = snes' in profile.read_text(),'F12 switch back failed'
                key(114);key(123);shot('native-music-tree');key(123)
            else:
                click(154,295);click(154,324);click(174,436);click(194,464)
                USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))
                USER32.PostMessageW(hwnd,0x20a,((-480)&65535)<<16,300|(500<<16));time.sleep(.5)
                shot('inactive-terrain-tree');key(123)
        finally:
            if process.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
    assert process.returncode==0
    assert (out/'game.log').read_text().count('Loading '+name)>=(3 if level==3 else 2),'Audio apply did not invoke the original level loader'
    positions=[]
    for slot in ((1,2,3) if level==3 else (1,2)):
        state=out/f'tlk_slot{slot}.state';frame=struct.unpack_from('<I',state.read_bytes(),12)[0]+1
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(out))
        cmd=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),'--load',str(state),'--frames',str(frame)]
        with (out/f'slot{slot}.log').open('wb') as f:subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
        ram=(out/f'hl_wram_{frame}.bin').read_bytes();w=lambda a:struct.unpack_from('<H',ram,a)[0]
        assert w(0x1ff9e)==level and w(0xdf)==descriptor,'Audio apply changed to a different level'
        positions.append([w(0xb21b),w(0xb21d)])
    if level==2:assert positions[0]!=positions[1],'Player position did not restart'
    tracks=[int(r['value']) for r in csv.DictReader((out/'commands.csv').open()) if r['selector']=='1'];assert track in tracks
    (out/'report.json').write_text(json.dumps({'result':'PASS','actual_f12_choice_persisted':True,'switched_back_to_native':level==3,'restarted_same_level':level,'before_after_positions':positions,'original_md_track_queued':track},indent=2)+'\n')
    print('Actual F12',name,'music switch restarts the same level PASS',flush=True)


if __name__=='__main__':main()
