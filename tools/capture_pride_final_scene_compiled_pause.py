"""Pause the real resource window during menu hold and incoming Continue fade."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import wave
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client

def pcm(path):
    with wave.open(str(path),'rb') as f:return f.readframes(f.getnframes())

def main():
    base=ROOT/'build/pride-final-scene-compiled-probe';out=base/'pause';out.mkdir()
    bound(base/'build-report.json');reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(reference)
    control=ROOT/'build/pride-continue-transition-edge-probe/pixel-checks/600'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];checks={};observations={}
    for age in (100,420):
        folder=out/str(age);folder.mkdir();cmd=report['commands'][1].copy();cmd[0]=str(base/'player.exe');cmd.remove('--lle')
        cmd[cmd.index('--load')+1]=str(ROOT/'build/pride-final-continue-fixture/prefatal.state')
        i=cmd.index('--dump-window');del cmd[i:i+2]  # This flag auto-exits a scripted paused window.
        for flag,filename in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd+=['--menu-at',str(3894+age),'--menu-page','resources']
        trace=folder/'tree.jsonl';timeline=folder/'exit.csv'
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_BANK_RECORD=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'),
            TLK_CONTINUE_EXIT_LOG=str(timeline),TLK_SOFT_TREE_LOG=str(trace))
        with (folder/'run.log').open('wb') as log:
            process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                until=time.monotonic()+45
                while process.poll() is None and time.monotonic()<until:
                    row=latest(trace)
                    if row and row['menu']==1 and row['about']==2:break
                    time.sleep(.02)
                else:raise AssertionError(('pause not reached',process.poll(),latest(trace)))
                hwnd=window_for(process.pid);assert hwnd
                USER32.SetProcessDPIAware();capture_client(hwnd,folder/'paused.png')
                before=latest(trace);guest=timeline.read_bytes();presentations=len(trace.read_bytes().splitlines())
                time.sleep(1.2)
                after=latest(trace);capture_client(hwnd,folder/'held.png')
                checks[f'{age}/time_frozen']=before['field']==after['field']==3894+age
                checks[f'{age}/guest_timeline_frozen']=timeline.read_bytes()==guest
                checks[f'{age}/presents_while_paused']=len(trace.read_bytes().splitlines())>presentations
                checks[f'{age}/no_source_edits']=after['dirty']==0
                scan=USER32.MapVirtualKeyW(0x7b,0)  # F12 closes the resource page and whole pause menu.
                assert USER32.PostMessageW(hwnd,0x100,0x7b,1+(scan<<16))
                assert USER32.PostMessageW(hwnd,0x101,0x7b,0xc0000001+(scan<<16))
                process.wait(timeout=60);assert process.returncode==0
                observations[str(age)]=dict(before=before,after=after)
            finally:
                if process.poll() is None:process.terminate();process.wait(timeout=5)
        checks[f'{age}/resume_guest']=hashes(folder/'run.log')==hashes(control/'run.log')
        checks[f'{age}/resume_pcm']=pcm(folder/'audio.wav')==pcm(control/'audio.wav')
        commands.append(cmd);print(age,'pause/resume checked',flush=True)
    source=[Path(__file__),base/'build-report.json',reference,ROOT/'tools/windows_capture.py']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks',flush=True);assert all(checks.values()),checks

if __name__=='__main__':main()
