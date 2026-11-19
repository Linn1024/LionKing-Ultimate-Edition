"""Apply each artwork/palette combination through the real paused resource tree."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-continue-token47';source=base/'artwork-verification/report.json';prior=bound(source)
    out=base/'live-ui';out.mkdir();cmd=prior['commands']['both'].copy();cmd.remove('--no-pace');cmd[cmd.index('--frames')+1]='6000'
    for flag,name in [('--dump-window','final.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=out/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    trace=out/'tree.jsonl';env['TLK_SOFT_TREE_LOG']=str(trace);checks={};snapshots={};hwnd=None
    USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate):
            deadline=time.monotonic()+30
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.01)
            raise AssertionError(('window state not reached',latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra)
            time.sleep(.06)
        def choice(row,name):return next(r for r in row['choices'] if r[0]==name)
        prefix='graphics.sprites.pickups.continue_token'
        def select(name):
            key(0x24)
            for _ in range(150):
                row=latest(trace);selected=row['choices'][row['selected']][0]
                if selected==name:return row
                if name.startswith(selected+'.') or selected=='game':key(0x27)
                key(0x28)
            raise AssertionError(('node unreachable',name))
        def setchoice(name,value):
            select(name)
            for _ in range(3):
                if choice(latest(trace),name)[1]==value:return
                key(0x0d)
            assert choice(latest(trace),name)[1]==value
        try:
            wait(lambda r:r['field']>=2520);hwnd=window_for(proc.pid);assert hwnd
            key(0x7b);row=wait(lambda r:r['about']==2);paused=row['field']
            checks['genuine_pride_loaded']=row['level']==0 and row['health']>0 and paused>=2520
            for label,frames,palette in [('native',1,1),('frames',2,1),('palette',1,2),('both',2,2)]:
                setchoice(prefix+'.frames',frames);setchoice(prefix+'.palette',palette)
                key(0x71);wait(lambda r:r['modal']==1);key(0x1b)
                row=select(prefix);snapshots[label]=row;capture_client(hwnd,out/(label+'.png'))
                checks[label+'_applied_live_without_restart']=row['dirty']==0 and row['field']==paused and row['about']==2
                checks[label+'_independent_choices']=choice(row,prefix+'.frames')[-1]==frames and choice(row,prefix+'.palette')[-1]==palette
                checks[label+'_profile_persisted']=all(prefix+'.'+part+' = '+('md' if value==2 else 'snes') in (out/'resources.ini').read_text() for part,value in [('frames',frames),('palette',palette)])
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
                operating_only_own_child_window=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
