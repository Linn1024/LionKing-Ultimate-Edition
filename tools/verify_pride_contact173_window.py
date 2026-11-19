"""Own real Windows client near the fresh rolling-contact sample."""
import json
import os
from pathlib import Path
import struct
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client
reference=ROOT/'build/pride-contact172-modes/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/pride-contact173-window';out.mkdir();cmd=r['commands']['long-roll-chase-aot'].copy()
source_tape=Path(cmd[cmd.index('--input')+1]);tape=out/'contact-pause.tape'
tape.write_bytes(source_tape.read_bytes()[:2576*2]+struct.pack('<'+'H'*201,0x1000,*([0]*200)))
cmd[cmd.index('--input')+1]=str(tape);cmd[cmd.index('--frames')+1]='6000';cmd.remove('--no-pace')
for flag in ('--dump-window','--dump-scene','--wav','--wav-seconds','--hash-at'):
    if flag in cmd:i=cmd.index(flag);del cmd[i:i+2]
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
trace=out/'tree.jsonl';env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=str(trace)
checks={};hwnd=None;USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate):
        end=time.monotonic()+60
        while proc.poll() is None and time.monotonic()<end:
            row=latest(trace)
            if row and predicate(row):return row
            time.sleep(.02)
        raise AssertionError(('contact window timeout',proc.poll(),latest(trace)))
    try:
        row=wait(lambda r:r['field']>=2584 and r['descriptor']==0xc00387 and r['health']>0)
        hwnd=window_for(proc.pid);assert hwnd;capture_client(hwnd,out/'contact.png')
        vk=0x7b;scan=USER32.MapVirtualKeyW(vk,0)
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16));assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16))
        menu=wait(lambda r:r['about']==2);capture_client(hwnd,out/'resources.png')
        choice=lambda name:next(c[-1] for c in menu['choices'] if c[0]==name)
        checks['actual_owned_pride_client']=row['descriptor']==0xc00387 and row['level']==0 and row['health']>0
        checks['original_md_view_and_body_choices']=menu['width']==320 and choice('display.viewport')==choice('gameplay.hitboxes.simba')==choice('gameplay.hitboxes.enemies')==2
        checks['independent_initialization_choices']=choice('gameplay.levels.pride_lands.activation')==choice('gameplay.levels.pride_lands.lizard_reactivation')==2
        checks['real_resource_menu']=menu['about']==2
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference,source_tape,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,row=row,menu=menu,
    scope='Real current139 SDL client near the verified contact. Ordinary Start input appended to the sampled prefix for capture. Native artwork/audio with independently selected MD geometry. Original comparison and sample hashes are172/171, not inferred from screenshots.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
