"""Select both Sun behavior sources through F12 and resume normal gameplay."""
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
    base=ROOT/'build/pride-continue-token-behavior50';source=base/'pickup-approach/report.json';prior=bound(source)
    out=base/'behavior-ui2';out.mkdir();cmd=prior['commands']['fresh-seed'].copy()
    i=cmd.index('--save-at');del cmd[i:i+3]
    cmd+=['--load',str(source.parent/'fresh-seed/saved.state'),'--menu-at','2510','--menu-page','resources']
    cmd[cmd.index('--frames')+1]='15000';cmd[cmd.index('--input-polled')+1]=str(ROOT/prior['selected']['tail_tape'])
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=out/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    for flag,name in [('--dump-window','final.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    i=cmd.index('--dump-window');del cmd[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};trace=out/'tree.jsonl';clean['TLK_SOFT_TREE_LOG']=str(trace)
    checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate,timeout=30):
            deadline=time.monotonic()+timeout
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.01)
            raise AssertionError(('UI state not reached',proc.poll(),latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
        def select(name):
            key(0x24)
            for _ in range(180):
                row=latest(trace);selected=row['choices'][row['selected']][0]
                if selected==name:return row
                if selected=='game' or name.startswith(selected+'.'):key(0x27)
                key(0x28)
            raise AssertionError(('node unreachable',name))
        names=('audio.effects.world.continue_token','gameplay.levels.pride_lands.continue_token_animation')
        try:
            before=wait(lambda r:r['about']==2 and r['field']==2510);hwnd=window_for(proc.pid);assert hwnd
            snapshots['before']=before;checks['current_build_gameplay_opened']=before['level']==0 and before['health']>0
            for label,name in zip(('voice','timing'),names):
                row=select(name)
                for _ in range(3):
                    if latest(trace)['choices'][row['selected']][1]==2:break
                    key(0x0d)
                snapshots[label+'-draft']=latest(trace);capture_client(hwnd,out/(label+'-draft.png'))
            key(0x71);wait(lambda r:not r['menu'] and r['field']<1000,15)
            after=wait(lambda r:r['field']>=2000 and r['descriptor']==0xc00387,60)
            snapshots['after']=after;capture_client(hwnd,out/'restarted-gameplay.png')
            checks['both_choices_applied']=all(next(r for r in after['choices'] if r[0]==name)[-1]==2 for name in names)
            checks['both_choices_persisted']=all(name+' = md' in (out/'resources.ini').read_text() for name in names)
            checks['ordinary_restart_playable']=after['level']==0 and after['health']==4 and after['lives']=={0:8,1:2,2:0}[after['difficulty']]
            checks['restart_inputs_finished']=after['macro_index']==after['macro_length']
            key(0x7b);wait(lambda r:r['about']==2);select(names[1]);capture_client(hwnd,out/'applied-timing.png')
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
                operates_only_own_child_window=True,cross_build_save_compatibility_tested=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
