"""Capture actual Windows gameplay and F12 from the genuine pre-response save."""
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
    base=ROOT/'build/pride-walking-response';source=base/'report.json';prior=bound(source)
    qualified=base/'qualification/report.json';assert bound(qualified)['result']=='PASS'
    out=base/'presentation';out.mkdir();cmd=prior['commands']['pre-cold'].copy()
    cmd.remove('--no-pace')
    for flag,name in [('--dump-window','final.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=out/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    trace=out/'tree.jsonl';env['TLK_SOFT_TREE_LOG']=str(trace)
    USER32.SetProcessDPIAware();checks={};hwnd=None;row=None
    profile=digest(out/'resources.ini')
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+30
            while proc.poll() is None and time.monotonic()<deadline:
                hwnd=window_for(proc.pid);row=latest(trace)
                if hwnd and row and row['field']>=3961:break
                time.sleep(.01)
            assert hwnd and row and row['field']>=3961
            capture_client(hwnd,out/'gameplay.png')
            checks['actual_pride_during_response']=row['level']==0 and row['health']>0
            scan=USER32.MapVirtualKeyW(0x7b,0)
            USER32.PostMessageW(hwnd,0x100,0x7b,1+(scan<<16));USER32.PostMessageW(hwnd,0x101,0x7b,0xc0000001+(scan<<16))
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and row['about']==2:break
                time.sleep(.01)
            assert row['about']==2;time.sleep(.2);capture_client(hwnd,out/'resources.png')
            checks['actual_resource_tree']=row['about']==2
            checks['md_attack_choice_active']=next(r for r in row['choices'] if r[0]=='gameplay.levels.pride_lands.porcupine_attack')[-1]==2
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    checks['profile_preserved']=digest(out/'resources.ini')==profile
    checks['real_state_loaded']='loaded_state=' in (out/'run.log').read_text()
    paths=[Path(__file__),source,qualified]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,process=proc.pid,
                operating_only_own_child_window=True,tree=row,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
