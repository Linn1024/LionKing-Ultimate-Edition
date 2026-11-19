"""Select checkpoint timing through the real Windows resource tree and restart."""
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
    base=ROOT/'build/pride-checkpoint-animation52';source=base/'animation-play/report.json';prior=bound(source)
    # Retain the rejected absolute third-cycle display assumption. This UI gate
    # checks source application/restart, not original field-for-field timing.
    assert [k for k,v in prior['checks'].items() if not v]==['display_3729']
    out=base/'windows-ui';out.mkdir();cmd=prior['commands']['snes-contact'].copy()
    for flag,count in [('--save-at',3),('--hash-at',2),('--dump-window',2),('--input-polled',2)]:
        i=cmd.index(flag);del cmd[i:i+count]
    cmd+=['--load',str(source.parent/'snes-contact/contact.state'),'--menu-at','3293','--menu-page','resources']
    cmd[cmd.index('--frames')+1]='15000'
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=out/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    for flag,name in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    trace=out/'tree.jsonl';clean['TLK_SOFT_TREE_LOG']=str(trace)
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
        name='gameplay.levels.pride_lands.checkpoint_animation'
        try:
            before=wait(lambda r:r['about']==2 and r['field']==3293);hwnd=window_for(proc.pid);assert hwnd
            snapshots['before']=before
            checks['current_build_gameplay_opened']=before['level']==0 and before['health']>0
            row=select(name)
            for _ in range(3):
                if latest(trace)['choices'][row['selected']][1]==2:break
                key(0x0d)
            snapshots['draft']=latest(trace);capture_client(hwnd,out/'draft.png')
            key(0x71);wait(lambda r:not r['menu'] and r['field']<1000,15)
            after=wait(lambda r:r['field']>=2000 and r['descriptor']==0xc00387 and r['health']>0
                       and r['macro_index']==r['macro_length'],60)
            snapshots['after']=after;capture_client(hwnd,out/'restarted-gameplay.png')
            checks['md_choice_applied']=next(r for r in after['choices'] if r[0]==name)[-1]==2
            checks['md_choice_persisted']=name+' = md' in (out/'resources.ini').read_text()
            checks['difficulty_preserved']=after['difficulty']==before['difficulty']
            checks['ordinary_restart_playable']=after['level']==0 and after['health']>0 and after['lives']>0
            checks['restart_inputs_finished']=after['macro_index']==after['macro_length']
            key(0x7b);wait(lambda r:r['about']==2);select(name);capture_client(hwnd,out/'applied.png')
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
                operates_only_own_child_window=True,cross_build_save_compatibility_tested=False,
                original_display_clock_equivalence_claimed=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
