"""Real native-timing MD Continue cursor/hold/exit/credit and retirement views."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from windows_capture import capture_client

reference=ROOT/'build/pride-menu210-continue/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu215-native-art/build-report.json';bound(build)
out=ROOT/'build/pride-menu217-windows';out.mkdir();checks={};commands={};observations={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
USER32.SetProcessDPIAware()
columns='kind,field,pc,scene,health,spares,credits,difficulty,brightness,choice,timer,padheld,padedge,action,entry,age,stack'.split(',')
def latest_frame(path):
    try:
        with path.open('rb') as f:f.seek(0,2);f.seek(max(0,f.tell()-8192));lines=f.read().splitlines()
        for line in reversed(lines):
            cells=line.decode().split(',')
            if len(cells)==len(columns) and cells[0]=='frame':return dict(zip(columns,[cells[0]]+list(map(int,cells[1:]))))
    except (OSError,ValueError,UnicodeError):pass
    return None
for case,targets in (
    ('idle',[('idle',4370)]),
    ('yes',[('ready',4400),('hold',4510),('exit-pose',4570),('retained-credit',4680),('resumed-level',4905)]),
    ('no',[('selected-no',4480),('fade',4545),('after-menu',4830)])):
    folder=out/case;folder.mkdir();cmd=ref['commands'][case].copy();cmd[0]=str(build.parent/'player.exe')
    for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds'):
        i=cmd.index(flag);del cmd[i:i+2]
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    trace=folder/'menu.csv';env=dict(clean,TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(trace))
    observations[case]={};hwnd=None
    with (folder/'run.log').open('wb') as f:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for name,target in targets:
                row=None;deadline=time.monotonic()+150
                while proc.poll() is None and time.monotonic()<deadline:
                    current=latest_frame(trace)
                    if current and current['field']>=target:
                        row=current;hwnd=window_for(proc.pid)
                        if hwnd:break
                    time.sleep(.003)
                assert row and hwnd,(case,name,proc.poll(),latest_frame(trace))
                capture_client(hwnd,folder/(name+'.png'));after=latest_frame(trace)
                observations[case][name]=dict(before=row,after=after)
                checks[case+'-'+name+'_actual_window_clock']=target<=row['field']<target+8
                print(case,name,row['field'],after['field'],flush=True)
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks[case+'_clean_exit']=proc.returncode==0;commands[case]=cmd
    pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
    actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(reference.parent/case/'run.log').read_text())
    checks[case+'_observed_guest_prefix_exact']=len(actual)>800 and actual==expected[:len(actual)]
checks['yes_credit_consumed_in_guest_while_art_retains_count']=observations['yes']['retained-credit']['before']['credits']==0
checks['yes_resumed_native_level']=observations['yes']['resumed-level']['before']['scene']==0xc00387 and observations['yes']['resumed-level']['before']['health']==4
paths=[Path(__file__),reference,build,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
    scope='Actual native-timing MD-art Continue idle/YES/NO Windows clients with guest-prefix preservation, live cursor, confirmation hold/exit, retained pre-consumption credit and ownership retirement. Complete pixel checks separate. No public/320/save/source-switch claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
