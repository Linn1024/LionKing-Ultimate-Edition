"""One actual Windows capture of the corrected stationary falling-letter title."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride-caption270-clamp/report.json';ref=bound(reference)
out=ROOT/'build/pride-caption271-window';out.mkdir()
cmd=ref['commands']['320-snes-1050-new'].copy();cmd.remove('--no-pace')
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--frames')+1]='1500'
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
USER32.SetProcessDPIAware();hwnd=None;reader=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+60
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=1030:
                hwnd=window_for(proc.pid)
                if hwnd:break
            time.sleep(.005)
        assert hwnd
        capture_client(hwnd,out/'caption.png');after=reader.snapshot()
    finally:
        if reader:reader.close()
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks=dict(actual_opening_caption_interval=1030<=before['field']<=after['field']<1150,clean_exit=proc.returncode==0)
paths=[Path(__file__),reference,ROOT/'tools/windows_capture.py',ROOT/'tools/pride_process_read.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,
    scope='One actual Windows native-art opening title at320 with stationary camera; visual centring inspected. No unrelated regression suite.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',before['field'],after['field'],flush=True)
