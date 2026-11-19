"""Pause the real resource menu during the arrival chime and resume exactly."""
import json
import os
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_soft_tree import latest
from verify_windows import USER32, window_for
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-arrival-work/player'
    bp=base/'build-report.json';bound(bp)
    rp=base/'arrival-audio/report.json';assert bound(rp)['result']=='PASS'
    out=base/'arrival-pause';out.mkdir()
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\naudio.effects.world.pickup_arrival = md\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';trace=out/'tree.jsonl'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_SOFT_TREE_LOG=str(trace),TLK_PICKUP_ARRIVAL_TRACE=str(out/'arrival.csv'),
               TLK_MD_SOUND_COMMANDS=str(out/'driver.csv'))
    command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
        '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,
        '--input-polled',tape,'--frames',2000,'--menu-at',1676,'--menu-page','resources',
        '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,2001))),
        '--wav',out/'audio.wav','--wav-seconds',60]))
    checks={};snapshots={}
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+90
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and row['menu']==1 and row['about']==2:break
                time.sleep(.02)
            else:raise AssertionError(('menu not reached',proc.poll(),latest(trace)))
            hwnd=window_for(proc.pid);assert hwnd
            USER32.SetProcessDPIAware()
            def key(value):
                scan=USER32.MapVirtualKeyW(value,0);extra=0x1000000 if 0x21<=value<=0x28 else 0
                assert USER32.PostMessageW(hwnd,0x100,value,1+(scan<<16)+extra)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001+(scan<<16)+extra)
                time.sleep(.06)
            node='audio.effects.world.pickup_arrival'
            key(0x24)
            for _ in range(150):
                row=latest(trace);selected=row['choices'][row['selected']][0]
                if selected==node:break
                if node.startswith(selected+'.') or selected=='game':key(0x27)
                key(0x28)
            else:raise AssertionError('arrival node missing')
            row=latest(trace);snapshots['selected']=row
            choice=next(c for c in row['choices'] if c[0]==node)
            checks['independent_leaf_selected_and_active']=choice[2]==2 and choice[4]==2
            capture_client(hwnd,out/'paused.png')
            before=len(trace.read_bytes().splitlines());time.sleep(1.2)
            row=latest(trace);snapshots['held']=row
            checks['repeated_presentations']=len(trace.read_bytes().splitlines())>before
            checks['guest_stays_at_tail_pause']=all(r['field']==1676 for r in snapshots.values())
            checks['no_pending_edits']=row['dirty']==0
            key(0x1b);key(0x1b);key(0x1b)
            proc.wait(timeout=120);assert proc.returncode==0
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    control=base/'arrival-audio/arrival-aot'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:re.findall(pattern,p.read_text())
    checks['every_guest_field']=len(rows(out/'run.log'))==2000 and rows(out/'run.log')==rows(control/'run.log')
    checks['entire_pcm']=wav_data(out/'audio.wav')==wav_data(control/'audio.wav')
    checks['original_entry_counts']= (out/'arrival.csv').read_bytes()==(control/'arrival.csv').read_bytes()
    checks['driver_commands']= (out/'driver.csv').read_bytes()==(control/'driver.csv').read_bytes()
    paths=[Path(__file__),bp,rp,ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=command,snapshots=snapshots,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True);assert all(checks.values())


if __name__=='__main__':main()
