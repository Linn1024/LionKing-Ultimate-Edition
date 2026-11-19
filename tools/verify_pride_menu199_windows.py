"""Inspect current139 Game Over at the measured menu-loop clocks in real Windows."""
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
from verify_windows import USER32, window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client

reference = ROOT/'build/pride-menu198-clocks/report.json'
ref = bound(reference)
assert ref['result']=='PASS'
out = ROOT/'build/pride-menu199-windows'
out.mkdir()
checks = {}
commands = {}
observations = {}
clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
USER32.SetProcessDPIAware()
for source in ('snes','md'):
    folder = out/source
    folder.mkdir()
    cmd = ref['commands'][source+'-aot'].copy()
    for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds'):
        i = cmd.index(flag);del cmd[i:i+2]
    for flag, filename in (('--config','host.ini'),('--resource-profile','resources.ini')):
        target = folder/filename
        target.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1] = str(target)
    first = int(ref['observations'][source]['first_callbacks']['FinalInputDecision']['field'])
    trace = folder/'tree.jsonl'
    with (folder/'run.log').open('wb') as f:
        proc = subprocess.Popen(cmd,cwd=ROOT,env=dict(clean,TLK_SOFT_TREE_LOG=str(trace)),
            stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd = None
        row = None
        try:
            deadline = time.monotonic()+180
            while proc.poll() is None and time.monotonic()<deadline:
                current = latest(trace)
                if current and current['field']>=first+12:
                    row=current;hwnd=window_for(proc.pid)
                    if hwnd:break
                time.sleep(.008)
            assert row and hwnd,(source,proc.poll(),latest(trace))
            capture_client(hwnd,folder/'game-over.png')
            checks[source+'_actual_menu_window'] = (row['field']<first+70 and row['health']==0 and
                row['lives']==0 and row['descriptor']==0xc0057b and row['menu']==0)
            observations[source] = dict(first_decision_field=first,tree_before_capture=row)
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks[source+'_clean_exit'] = proc.returncode==0
    pattern = r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual = re.findall(pattern,(folder/'run.log').read_text())
    expected = re.findall(pattern,(reference.parent/source/'aot/run.log').read_text())
    checks[source+'_observed_guest_prefix_exact'] = len(actual)>first-4000 and actual==expected[:len(actual)]
    commands[source]=cmd
    print(source,'Windows menu',row['field'] if row else None,'exit',proc.returncode,flush=True)
paths=[Path(__file__),reference,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,commands=commands,observations=observations,
    scope='Actual own-child current139 Windows native-art Game Over clients at measured native/MD '
          'timeline menu-loop clocks, fresh ordinary power-on controls and matching guest prefix. '
          'No independently selected MD artwork or cross-console pixel equivalence claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
