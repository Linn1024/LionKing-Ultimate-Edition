"""Load a genuine non-Pride save while a Pride revival owns presentation."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import read_rows
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-launch3';bp=base/'build-report.json';build=bound(bp);out=base/'owned-exit';out.mkdir()
    state=base/'scene-saves/level1-aot/scene.state';slot=out/'tlk_slot1.state';shutil.copy2(state,slot);before=digest(slot)
    profile=out/'resources.ini';profile.write_bytes((ROOT/'profiles/pride-development-preview.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    common=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--input',tape,'--frames',2700,'--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,2701)))]
    for name in ('control','live'):
        folder=out/name;folder.mkdir();config=out/(name+'.ini');config.write_text('opengl = 0\nscale = 2\n')
        cmd=common+['--config',config,'--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        cmd+=['--load',state,'--no-pace'] if name=='control' else ['--practice-level',0]
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            if name=='control':r=subprocess.run(commands[name],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180);assert not r.returncode
            else:
                trace=folder/'presents.jsonl';env=dict(clean,TLK_PRIDE_DIAGNOSTICS=str(folder),TLK_SOFT_TREE_LOG=str(trace))
                proc=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                deadline=time.monotonic()+120;hwnd=None
                try:
                    while not hwnd and proc.poll() is None and time.monotonic()<deadline:hwnd=window_for(proc.pid);time.sleep(.01)
                    assert hwnd
                    while proc.poll() is None and time.monotonic()<deadline:
                        events=[r for r in read_rows(folder/'owner-events.csv') if r['event']=='begin'];row=latest(trace)
                        if events and row and row['field']>=int(events[0]['field'])+100:break
                        time.sleep(.005)
                    else:raise AssertionError(('No owned scene',proc.poll(),latest(trace)))
                    owned_field=row['field'];USER32.SetProcessDPIAware();capture_client(hwnd,folder/'before-load.png')
                    assert USER32.PostMessageW(hwnd,0x100,0x74,1) and USER32.PostMessageW(hwnd,0x101,0x74,0xc0000001)
                    while proc.poll() is None and time.monotonic()<deadline:
                        row=latest(trace)
                        if row and row['field']<owned_field:break
                        time.sleep(.005)
                    assert row and 1600<=row['field']<1615,row
                    time.sleep(.1);capture_client(hwnd,folder/'after-load.png');proc.wait(timeout=90);assert not proc.returncode
                finally:
                    if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';rows=lambda name:re.findall(pattern,(out/name/'run.log').read_text())
    actual=rows('live');rewinds=[i for i in range(1,len(actual)) if int(actual[i][0])<int(actual[i-1][0])];assert len(rewinds)==1,rewinds
    tail=actual[rewinds[0]:];audio=wav_data(out/'control/audio.wav');loads=read_rows(out/'live/live-load.csv')
    checks=dict(owned_scene_observed=owned_field>=int(events[0]['field'])+100,
                actual_native_load=any(r['loaded_field']=='1600' and r['success']=='1' for r in loads),
                all_post_load_fields=tail==rows('control') and len(tail)==1100,
                entire_post_load_pcm=wav_data(out/'live/audio.wav')[-len(audio):]==audio,
                whole_guest=pixels(out/'live/guest.png')==pixels(out/'control/guest.png'),
                whole_client=pixels(out/'live/window.png')==pixels(out/'control/window.png'),
                slot_preserved=digest(slot)==before and slot.read_bytes()==state.read_bytes())
    for p in out.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(p)],stdout=subprocess.DEVNULL,check=True,timeout=60)
    paths=[Path(__file__),bp,state,base/'scene-saves/audit.json',ROOT/'profiles/pride-development-preview.ini',tape,*[ROOT/'tools'/n for n in ('verify_pride_audio_state.py','verify_pride_live_error_ui.py','verify_pride_soft_tree.py','verify_windows.py','windows_capture.py')]]
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=len(tail),owned_field=owned_field,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
