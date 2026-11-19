"""Real Windows native-timing private MD Game Over, fade and later title."""
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
from verify_pride_soft_tree import latest
from windows_capture import capture_client

reference = ROOT/'build/pride-menu198-clocks/report.json'
ref = bound(reference)
build_path = ROOT/'build/pride-menu200-native-art/build-report.json'
bound(build_path)
out = ROOT/'build/pride-menu202-art-windows'
out.mkdir()
checks = {}
observations = {}
cmd = ref['commands']['snes-aot'].copy()
cmd[0] = str(build_path.parent/'player.exe')
for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds'):
    i=cmd.index(flag);del cmd[i:i+2]
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
    cmd[cmd.index(flag)+1]=str(out/file)
clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
trace=out/'tree.jsonl'
env=dict(clean,TLK_SOFT_TREE_LOG=str(trace),TLK_MENU197=str(out/'menu.csv'),TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU200='1')
USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as f:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    hwnd=None
    try:
        for name,target in [('idle',4910),('fade',5424),('after-menu',5710)]:
            deadline=time.monotonic()+150
            row=None
            while proc.poll() is None and time.monotonic()<deadline:
                current=latest(trace)
                if current and current['field']>=target:
                    row=current;hwnd=window_for(proc.pid)
                    if hwnd:break
                time.sleep(.003)
            assert row and hwnd,(name,proc.poll(),latest(trace))
            capture_client(hwnd,out/(name+'.png'))
            after=latest(trace)
            observations[name]=dict(before=row,after=after)
            checks[name+'_actual_window_clock']=target<=row['field']<target+8
            print(name,row['field'],after['field'],flush=True)
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['clean_exit']=proc.returncode==0
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
actual=re.findall(pattern,(out/'run.log').read_text())
expected=re.findall(pattern,(reference.parent/'snes/aot/run.log').read_text())
checks['observed_guest_prefix_exact']=len(actual)>1700 and actual==expected[:len(actual)]
paths=[Path(__file__),reference,build_path,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,command=cmd,observations=observations,
    scope='Private native-timing installed MD Game Over visible idle/fade and later native title. '
          'Exact guest prefix; visual pixel qualification separate. No Continue/public capability claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
