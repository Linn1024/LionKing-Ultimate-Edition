"""Actual resource-driven320 Continue after the centre-anchor correction."""
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride-menu221-wide/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu226-integrated/build-report.json';bound(build)
out=ROOT/'build/pride-menu227-integrated-windows';out.mkdir();checks={};observations={}
cmd=ref['commands']['yes-aot'].copy();binary=build.parent/'player.exe';cmd[0]=str(binary)
for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds'):
    i=cmd.index(flag);del cmd[i:i+2]
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    text=Path(cmd[cmd.index(flag)+1]).read_text()
    if flag=='--resource-profile':text+='graphics.pride_final_menu = md\n'
    (out/file).write_text(text);cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
USER32.SetProcessDPIAware();hwnd=None;reader=None
with (out/'run.log').open('wb') as f:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(binary,proc.pid)
        for name,target in [('ready',4400),('hold',4510),('exit-pose',4570),('retained-credit',4680),('resumed-level',4905)]:
            deadline=time.monotonic()+150;row=None
            while proc.poll() is None and time.monotonic()<deadline:
                current=reader.snapshot()
                if current['field']>=target:
                    row=current;hwnd=window_for(proc.pid)
                    if hwnd:break
                time.sleep(.003)
            assert row and hwnd,(name,proc.poll())
            capture_client(hwnd,out/(name+'.png'));after=reader.snapshot();observations[name]=dict(before=row,after=after)
            checks[name+'_actual_resource_driven_window']=row['art_mode']==1 and row['transition_mode']==0 and target<=row['field']<target+10
            print(name,row,after['field'],flush=True)
    finally:
        if reader:reader.close()
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['clean_exit']=proc.returncode==0
checks['native_guest_credit_consumed_and_art_count_retained']=observations['retained-credit']['before']['credits_guest']==0 and observations['retained-credit']['before']['credits_art']==1
checks['renderer_retired_for_native_gameplay']=observations['resumed-level']['before']['active']==0 and observations['resumed-level']['before']['health']==4
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
actual=re.findall(pattern,(out/'run.log').read_text());expected=re.findall(pattern,(reference.parent/'yes-control/run.log').read_text())
checks['samewidth_public_guest_prefix_exact']=len(actual)>1400 and actual==expected[:len(actual)]
paths=[Path(__file__),build,reference,ROOT/'tools/pride_process_read.py',ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,command=cmd,
    scope='Current maintained source leaf drives actual320 MD-art native YES without development flags; read-only child data observation, guest prefix and visual views. Pixel correction verification separate; not published/full release qualified.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
