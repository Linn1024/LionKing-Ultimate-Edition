"""Real F12 menu-art edits and cold restarts from an owned native Continue."""
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
from verify_pride_soft_tree import latest
from windows_capture import capture_client
reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu226-integrated/build-report.json';bound(build)
out=ROOT/'build/pride-menu229-resource-ui';out.mkdir();checks={};snapshots={}
cmd=ref['command'].copy()
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
cmd+=['--menu-at','4400','--menu-page','resources']
trace=out/'tree.jsonl';env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=str(trace)
USER32.SetProcessDPIAware();hwnd=None;reader=None;node='graphics.pride_final_menu'
with (out/'run.log').open('wb') as f:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate,seconds=120):
        deadline=time.monotonic()+seconds
        while proc.poll() is None and time.monotonic()<deadline:
            row=latest(trace)
            if row and predicate(row):return row
            time.sleep(.008)
        raise AssertionError(('UI state missing',proc.poll(),latest(trace)))
    def key(vk):
        scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
        assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
    def select():
        key(0x24)
        for _ in range(180):
            row=latest(trace);name=row['choices'][row['selected']][0]
            if name==node:return row
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        raise AssertionError('Independent menu graphics node missing')
    def effective(row):return {c[0]:c[-1] for c in row['choices'] if c[0]!=node}
    try:
        before=wait(lambda r:r['field']==4400 and r['about']==2);hwnd=window_for(proc.pid);assert hwnd
        reader=PlayerRead(Path(cmd[0]),proc.pid);owned=reader.snapshot();snapshots['before']=before;snapshots['owned-menu']=owned
        checks['paused_owned_native_menu']=owned['active']==1 and owned['art_mode']==1 and owned['transition_mode']==0
        select();capture_client(hwnd,out/'initial-node.png')
        for value,label in ((1,'snes'),(2,'md')):
            select()
            for _ in range(4):
                row=latest(trace)
                if row['choices'][row['selected']][1]==value:break
                key(0x0d)
            draft=latest(trace);snapshots[label+'-draft']=draft
            checks[label+'_explicit_draft']=next(c for c in draft['choices'] if c[0]==node)[1]==value
            key(0x71);wait(lambda r:not r['menu'] and r['field']<1000)
            after=wait(lambda r:r['field']>=2200 and r['descriptor']==0xc00387 and r['health']>0 and r['macro_index']==r['macro_length'])
            state=reader.snapshot();snapshots[label+'-after']=after;snapshots[label+'-renderer']=state
            capture_client(hwnd,out/(label+'-gameplay.png'))
            checks[label+'_source_applied_and_persisted']=next(c[-1] for c in after['choices'] if c[0]==node)==value and node+' = '+label in (out/'resources.ini').read_text()
            checks[label+'_difficulty_and_other_resources_retained']=after['difficulty']==before['difficulty'] and effective(after)==effective(before)
            checks[label+'_native_owner_cleared_and_mode_refreshed']=state['active']==0 and state['credits_art']==0 and state['art_mode']==(value==2)
            key(0x7b);wait(lambda r:r['about']==2)
    finally:
        if reader:reader.close()
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference,build,ROOT/'tools/pride_process_read.py',ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
    scope='Actual resource node reached in F12, MD→SNES→MD commits from native Continue and restarted gameplay. Retained difficulty/all other effective nodes, native owner cleared, current mode read-only observed. Full release gates remain.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
