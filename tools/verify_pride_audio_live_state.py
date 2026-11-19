"""Exercise real F1/F5 audio continuation and atomic backend rejection."""
import csv
import json
import os
import struct
import subprocess
import time
from audit_scenes import ROOT
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client
from verify_pride_audio_state import audio_offset,seal,wav_data


def main():
    USER32.SetProcessDPIAware()
    out=ROOT/'build/pride-audio-live-state';out.mkdir(exist_ok=True)
    ready=ROOT/'build/pride-hyena-taunt/ready.state'
    zero=out/'zero.polled.tape';zero.write_bytes(bytes(10000))
    profile=out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.world.hyena_taunt = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
          '--config',str(config),'--input-polled',str(zero),'--no-audio','--no-record']
    results={}
    for mode in ('valid','rejected'):
        slot=out/'tlk_slot1.state';slot.unlink(missing_ok=True)
        (out/(mode+'.csv')).unlink(missing_ok=True)
        env=os.environ.copy();env['TLK_AUDIO_STEMS']=str(out/(mode+'.csv'))
        env['TLK_HYENA_TAUNT_TRACE']=str(out/(mode+'-entries.csv'))
        log=out/(mode+'.log')
        with log.open('wb') as stream:
            process=subprocess.Popen(base+['--load',str(ready),'--frames','4200','--wav',str(out/(mode+'.wav'))],
                                     cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            hwnd=None
            try:
                deadline=time.monotonic()+90
                def rows():
                    path=out/(mode+'.csv')
                    try:return [r for r in csv.DictReader(path.open()) if r.get('md_peak') is not None]
                    except (OSError,ValueError):return []
                while time.monotonic()<deadline:
                    hwnd=window_for(process.pid)
                    current=rows()
                    if hwnd and current and int(current[-1]['frame'])>=4028:break
                    assert process.poll() is None
                    time.sleep(.005)
                assert hwnd and current and int(current[-1]['frame'])<4040,'Missed the live voice fixture'
                def key(value):
                    assert USER32.PostMessageW(hwnd,0x100,value,1)
                    assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001)
                key(112)
                raw=None
                while raw is None:
                    assert time.monotonic()<deadline and process.poll() is None
                    try:raw=slot.read_bytes()
                    except (FileNotFoundError,PermissionError):time.sleep(.005)
                saved=struct.unpack_from('<I',raw,12)[0]
                assert 4028<=saved<4040
                capture_client(hwnd,out/(mode+'-saved.png'))
                checkpoint=out/(mode+'-checkpoint.state');checkpoint.write_bytes(raw)
                if mode=='rejected':
                    raw=bytearray(raw);at=audio_offset(raw)
                    md=at+128+struct.unpack_from('<I',raw,at+44)[0]
                    core=md+120+32768*4+struct.unpack_from('<I',raw,md+48)[0]*8
                    raw[core]^=1;slot.write_bytes(seal(raw))
                while True:
                    current=rows()
                    if current and int(current[-1]['frame'])>=4100:break
                    assert time.monotonic()<deadline and process.poll() is None
                    time.sleep(.005)
                key(116)
                time.sleep(.1)
                capture_client(hwnd,out/(mode+'-loaded.png'))
                process.wait(timeout=60)
            finally:
                if process.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
        assert process.returncode==0
        assert len(list(csv.DictReader((out/(mode+'-entries.csv')).open())))==1,'Load re-emitted initialized taunt'
        if mode=='valid':
            path=out/'expected.wav'
            with (out/'expected.log').open('wb') as stream:
                subprocess.run(base+['--load',str(checkpoint),'--frames',str(saved+20),'--no-pace',
                                     '--wav',str(path)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
            expected=wav_data(path);audio=wav_data(out/'valid.wav')
            occurrences=audio.count(expected)
            assert expected and occurrences>=2,('Live F5 did not reproduce the exact mixed continuation',occurrences)
            results[mode]={'saved_frame':saved,'exact_twenty_field_wav_occurrences':occurrences,'no_duplicate_taunt':True}
        else:
            path=out/'control.wav';control=out/'control.log'
            with control.open('wb') as stream:
                subprocess.run(base+['--load',str(ready),'--frames','4200','--no-pace','--wav',str(path)],
                               cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
            assert wav_data(path)==wav_data(out/'rejected.wav'),'Rejected live load changed audio timeline'
            assert hashes(control)==hashes(log),'Rejected live load changed guest timeline'
            results[mode]={'saved_frame':saved,'complete_wav_and_guest_equal_to_no_load_control':True}
        print(mode,'actual F1/F5 audio state PASS',flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'cases':results},indent=2)+'\n')


if __name__=='__main__':main()
