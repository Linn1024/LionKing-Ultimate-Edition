"""Inspect the precise checkpoint capability through its actual Windows UI."""
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
    base=ROOT/'build/pride-checkpoint-capability53';buildpath=base/'build-report.json';bound(buildpath)
    source=ROOT/'build/pride-checkpoint-animation52/animation-play/report.json';prior=bound(source)
    out=base/'windows-scope';out.mkdir();cmd=prior['commands']['md-contact'].copy();cmd[0]=str(base/'player.exe')
    for flag,count in [('--save-at',3),('--hash-at',2),('--dump-window',2)]:
        i=cmd.index(flag);del cmd[i:i+count]
    cmd+=['--menu-at','3293','--menu-page','resources'];cmd[cmd.index('--frames')+1]='15000'
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=out/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    for flag,name in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    trace=out/'tree.jsonl';clean['TLK_SOFT_TREE_LOG']=str(trace);hwnd=None;checks={};snapshots={}
    USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate,timeout=90):
            deadline=time.monotonic()+timeout
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.02)
            raise AssertionError(('UI state not reached',proc.poll(),latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
        try:
            snapshots['before']=wait(lambda r:r['about']==2 and r['field']==3293)
            hwnd=window_for(proc.pid);assert hwnd
            name='gameplay.levels.pride_lands.checkpoint_animation';key(0x24)
            for _ in range(180):
                row=latest(trace);selected=row['choices'][row['selected']][0]
                if selected==name:break
                if selected=='game' or name.startswith(selected+'.'):key(0x27)
                key(0x28)
            else:raise AssertionError('checkpoint node unreachable')
            capture_client(hwnd,out/'selected.png');key(0x48)
            scope=wait(lambda r:'native game update scheduling retained' in r['help'])
            snapshots['scope']=scope;capture_client(hwnd,out/'scope.png')
            checks['scope_has_original_update_durations']='6/21/6 updates' in scope['help']
            checks['scope_discloses_native_scheduling']='native game update scheduling retained' in scope['help']
            checks['scope_keeps_sources_independent']='Artwork, palette, sound and checkpoint coordinates are independent' in scope['help']
            checks['level_restart_disclosed']='restarts the level' in scope['help']
            checks['selected_source_md']=scope['choices'][scope['selected']][-1]==2
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),source,buildpath]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
                fresh_power_on=True,operates_only_own_child_window=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
