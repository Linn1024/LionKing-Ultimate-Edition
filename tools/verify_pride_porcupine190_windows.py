"""Own real Windows hit clients from actual pending-reaction current checkpoints."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';build=bound(bp)
reference=ROOT/'build/pride-porcupine186-polled/report.json';ref=bound(reference);assert ref['result']=='CAPTURED'
proof=ROOT/'build/pride-porcupine187-difficulty/report.json';assert bound(proof)['result']=='PASS'
out=ROOT/'build/pride-porcupine190-windows';out.mkdir();checks={};commands={};seen={};USER32.SetProcessDPIAware()
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for difficulty,spares in [('easy',8),('normal',2),('hard',0)]:
    folder=out/difficulty;folder.mkdir();hit=ref['cases'][difficulty]['porcupine_hits'][0]['field'];pending=hit-1
    state=folder/'pending.state';cmd=ref['commands'][difficulty].copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--frames')+1]=str(pending);cmd[cmd.index('--hash-at')+1]=str(pending)
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','seed-window.png'),('--dump-scene','seed-scene.json'),('--wav','seed-audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    cmd+=['--save-at',str(pending),str(state)]
    with (folder/'seed.log').open('wb') as f:p=subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode==0
    pattern=rf'frame={pending} frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    checks[difficulty+'_actual_pending_seed_guest_exact']=re.findall(pattern,(folder/'seed.log').read_text())==re.findall(pattern,(reference.parent/difficulty/'run.log').read_text())!=[]
    commands[difficulty+'-seed']=cmd.copy();i=cmd.index('--save-at');del cmd[i:i+3];cmd[cmd.index('--load')+1]=str(state)
    neutral=folder/'neutral.polled.tape';neutral.write_bytes(b'\0\0'*1000);cmd[cmd.index('--input-polled')+1]=str(neutral);cmd[cmd.index('--frames')+1]=str(hit+300);cmd.remove('--no-pace')
    for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds','--hash-at'):
        if flag in cmd:i=cmd.index(flag);del cmd[i:i+2]
    trace=folder/'tree.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace));hwnd=None;row=None
    with (folder/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+45
            while proc.poll() is None and time.monotonic()<deadline:
                current=latest(trace)
                if current and current['field']>=hit and current['health']==3 and current['descriptor']==0xc00387:
                    row=current;hwnd=window_for(proc.pid)
                    if hwnd:break
                time.sleep(.008)
            assert row and hwnd,(difficulty,'first-hit window missing',proc.poll(),latest(trace))
            capture_client(hwnd,folder/'hit.png')
            checks[difficulty+'_actual_health3_pride_client']=row['level']==0 and row['health']==3 and row['lives']==spares and row['field']<hit+30
            seen[difficulty]=row
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks[difficulty+'_clean_exit']=proc.returncode==0;commands[difficulty]=cmd;print(difficulty,'actual OS hit',row['field'] if row else None,flush=True)
checks['public139_binary_exact']=digest(base/'player.exe')==digest(ROOT/'dist/installed-preview139/LionKing.exe')==build['binary_sha256']
paths=[Path(__file__),bp,reference,proof,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=seen,
    scope='Current139 real own-child Windows clients at health3 on allthree real Options difficulties. Genuine per-source pending-reaction checkpoints have exact guest hashes before cold replay; no actor/health edits or old-build saves. Full observed difficulty sequence is187; production/mode verification is188. Images alone do not establish equal cross-source geometry.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
