"""Actual audio leaf draft, Apply/restart and resumed second-level Windows client."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait573-route-audio/report.json';r=bound(reference);build=ROOT/'build/cant-wait579/build-report.json';bound(build)
out=ROOT/'build/cant-wait581-audio-ui';out.mkdir(exist_ok=True);cmd=r['commands']['route'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,n in (('--save-at',3),('--input-polled',2),('--dump-window',2),('--wav',2)):
    i=cmd.index(flag);del cmd[i:i+n]
for flag,value in (('--frames','8000'),('--hash-at','1600'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
cmd+=['--menu-at','1600','--menu-page','resources']
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware();node='audio.effects.world.cant_wait.ostrich_steps'
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate,seconds=25):
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
        initial=wait(lambda r:r['about']==2 and r['field']==1600);hwnd=window_for(proc.pid);assert hwnd;snapshots['initial']=initial
        key(0x24)
        for _ in range(210):
            row=trace.latest();name=row['choices'][row['selected']][0]
            if name==node:break
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        assert name==node
        key(0x0d);key(0x0d);draft=wait(lambda r:choices(r)[node][1]==2);snapshots['draft']=draft
        checks['independent_paused_draft']=draft['field']==1600 and choices(draft)[node][4]==1 and choices(draft)['audio.effects.world.cant_wait.ostrich_jump'][3]==1
        capture_client(hwnd,out/'audio-options.png');key(0x71)
        restarted=wait(lambda r:not r['menu'] and r['field']<1600);snapshots['restart']=restarted
        after=wait(lambda r:not r['menu'] and r['field']>=1900 and r['descriptor']==0xc003b9 and r['health']>0 and r['macro_index']==r['macro_length']);snapshots['after']=after
        capture_client(hwnd,out/'gameplay.png');checks['playable_second_level_restart']=after['level']==1 and after['difficulty']==initial['difficulty']
        checks['persisted']=node+' = md' in (out/'resources.ini').read_text() and choices(after)[node][4]==2
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,trace_metadata=metadata,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
