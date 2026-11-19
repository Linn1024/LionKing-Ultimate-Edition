"""Actual second-level resource edit, live palette Apply and Windows capture."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait441-monkeys/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/cant-wait442-ui';out.mkdir(exist_ok=True);cmd=ref['commands']['native'].copy()
i=cmd.index('--dump-window');del cmd[i:i+2];cmd[cmd.index('--frames')+1]='8000';cmd+=['--menu-at','2200','--menu-page','resources']
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
cmd[cmd.index('--dump-scene')+1]=str(out/'scene.json')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware();node='graphics.sprites.animals.monkeys.palette'
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate,seconds=35):
        deadline=time.monotonic()+seconds
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row and predicate(row):return row
            time.sleep(.008)
        raise AssertionError(('UI wait',proc.poll(),trace.latest()))
    def key(vk):
        scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
        assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
    def choices(row):return {c[0]:c for c in row['choices']}
    try:
        initial=wait(lambda r:r['about']==2 and r['field']==2200);hwnd=window_for(proc.pid);assert hwnd;snapshots['initial']=initial
        key(0x24)
        for _ in range(180):
            r=trace.latest();name=r['choices'][r['selected']][0]
            if name==node:break
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        assert name==node
        key(0x0d);key(0x0d);draft=wait(lambda r:choices(r)[node][1]==2);snapshots['draft']=draft
        checks['independent_paused_draft']=draft['field']==initial['field'] and choices(draft)[node][4]==1 and choices(draft)['graphics.scenery.palettes'][4]==2
        capture_client(hwnd,out/'monkey-options.png');key(0x71);applied=wait(lambda r:choices(r)[node][4]==2);snapshots['applied']=applied
        checks['live_apply']=applied['field']==initial['field'];key(0x1b);key(0x1b);key(0x09)
        after=wait(lambda r:not r['menu'] and r['field']>=2250 and r['level']==1);snapshots['after']=after
        capture_client(hwnd,out/'monkeys.png');checks['actual_gameplay']=after['health']>0 and after['descriptor']==0xc003b9
        checks['persisted']='graphics.sprites.animals.monkeys.palette = md' in (out/'resources.ini').read_text()
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        trace_metadata=trace.finish()
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,trace_metadata=trace_metadata,scope='Actual SDL second-level animal palette node; paused draft, same-field live Apply, persistence, resumed real Windows client. No source restart, gameplay modification, old-save or unrelated matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
