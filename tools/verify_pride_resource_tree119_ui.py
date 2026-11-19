"""Actual group selection switches both inherited Continue-token children live."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client

base=ROOT/'build/pride-resource-tree118';bp=base/'build-report.json';bound(bp)
reference=ROOT/'build/pride-menu-enable86/route/report.json';prior=bound(reference)
out=base/'windows-ui119';out.mkdir();seed=out/'seed';seed.mkdir()
cmd=prior['commands']['menus-aot'].copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--frames')+1]='1200'
for flag in ('--hash-at','--dump-window'):i=cmd.index(flag);del cmd[i:i+2]
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    text=Path(cmd[cmd.index(flag)+1]).read_text()
    if file=='resources.ini':
        text='\n'.join(line for line in text.splitlines() if not line.startswith('graphics.sprites.pickups.continue_token'))+'\ngraphics.sprites.pickups.continue_token = snes\n'
    (seed/file).write_text(text);cmd[cmd.index(flag)+1]=str(seed/file)
for flag,file in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(seed/file)
cmd+=['--save-at','1200',str(seed/'current.state')]
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (seed/'run.log').open('wb') as f:subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
seed_command=cmd.copy()
for flag,count in [('--save-at',3),('--input-polled',2)]:i=cmd.index(flag);del cmd[i:i+count]
cmd.remove('--no-pace');cmd[cmd.index('--frames')+1]='18000';cmd+=['--load',str(seed/'current.state'),'--menu-at','1201','--menu-page','resources']
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
for flag,file in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
trace=out/'tree.jsonl';checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as f:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(clean,TLK_SOFT_TREE_LOG=str(trace)),stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate):
        end=time.monotonic()+60
        while proc.poll() is None and time.monotonic()<end:
            row=latest(trace)
            if row and predicate(row):return row
            time.sleep(.01)
        raise AssertionError(('UI condition',proc.poll(),latest(trace)))
    def key(vk):
        scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
        assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
    group='graphics.sprites.pickups.continue_token';children=[group+'.frames',group+'.palette']
    def choice(row,id):return next(c for c in row['choices'] if c[0]==id)
    def select():
        key(0x24)
        for _ in range(180):
            row=latest(trace);name=row['choices'][row['selected']][0]
            if name==group:return row
            if name=='game' or group.startswith(name+'.'):key(0x27)
            key(0x28)
        raise AssertionError('Continue-token group missing')
    def other(row):return {c[0]:c[-1] for c in row['choices'] if c[0] not in [group,*children]}
    try:
        before=wait(lambda r:r['about']==2 and r['field']==1201);hwnd=window_for(proc.pid);assert hwnd;snapshots['before']=before
        checks['options_md_does_not_leak_into_initial_art']=choice(before,'audio.effects.options_adjustment')[-1]==2 and all(choice(before,c)[-1]==1 for c in children)
        for label,value in [('md',2),('snes',1)]:
            row=select()
            for _ in range(4):
                if choice(latest(trace),group)[1]==value:break
                key(0x0d)
            draft=latest(trace);snapshots[label+'-draft']=draft
            checks[label+'_both_children_follow_draft_group']=all(choice(draft,c)[1]==0 and choice(draft,c)[3]==value for c in children)
            key(0x27);capture_client(hwnd,out/(label+'-draft.png'))
            key(0x71);applied=wait(lambda r:not r['dirty'] and choice(r,group)[-1]==value);snapshots[label+'-applied']=applied
            checks[label+'_applies_live_while_paused']=applied['menu']==1 and applied['field']==draft['field']
            checks[label+'_both_active_children_follow_group']=all(choice(applied,c)[1]==0 and choice(applied,c)[-1]==value for c in children)
            checks[label+'_other_choices_retained']=other(applied)==other(before)
            checks[label+'_source_persisted']=group+' = '+label in (out/'resources.ini').read_text()
            key(0x7b);after=wait(lambda r:not r['menu'] and r['field']>=draft['field']+20 and r['health']>0);snapshots[label+'-game']=after
            capture_client(hwnd,out/(label+'-game.png'));key(0x7b);wait(lambda r:r['about']==2)
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),bp,reference,ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,snapshots=snapshots,seed_command=seed_command,command=cmd,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('UI',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
