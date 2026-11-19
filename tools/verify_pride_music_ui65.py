"""Pause and switch music both ways through the real Windows resource tree."""
import csv
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
    base=ROOT/'build/pride-music-output65';bp=base/'build-report.json';build=bound(bp)
    source=base/'completion/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'windows-ui';out.mkdir();seed=out/'seed';seed.mkdir();cmd=prior['commands']['aot'].copy()
    cmd[cmd.index('--frames')+1]='1200'
    for flag,count in [('--hash-at',2),('--dump-window',2)]:i=cmd.index(flag);del cmd[i:i+count]
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (seed/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(seed/file)
    for flag,file in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(seed/file)
    cmd+=['--save-at','1200',str(seed/'current.state')]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    with (seed/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
    seed_command=cmd.copy()
    for flag,count in [('--save-at',3),('--input-polled',2)]:i=cmd.index(flag);del cmd[i:i+count]
    cmd.remove('--no-pace');cmd[cmd.index('--frames')+1]='18000'
    cmd+=['--load',str(seed/'current.state'),'--menu-at','1201','--menu-page','resources']
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
    for flag,file in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
    trace=out/'tree.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace),TLK_MD_SOUND_COMMANDS=str(out/'driver.csv'))
    checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate,timeout=60):
            end=time.monotonic()+timeout
            while proc.poll() is None and time.monotonic()<end:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.008)
            raise AssertionError(('UI condition missing',proc.poll(),latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
        node='audio.music.pride_lands'
        def select():
            key(0x24)
            for _ in range(180):
                row=latest(trace);name=row['choices'][row['selected']][0]
                if name==node:return row
                if name=='game' or node.startswith(name+'.'):key(0x27)
                key(0x28)
            raise AssertionError('Pride music node missing')
        def drivers():return list(csv.DictReader((out/'driver.csv').open()))
        def effective(row):return {c[0]:c[-1] for c in row['choices'] if c[0] not in ('game','audio','audio.music',node)}
        try:
            before=wait(lambda r:r['about']==2 and r['field']==1201);hwnd=window_for(proc.pid);assert hwnd
            snapshots['before']=before;select();capture_client(hwnd,out/'paused.png')
            size=(out/'audio.wav').stat().st_size;commands_before=len(drivers());time.sleep(1.1)
            held=latest(trace);snapshots['held']=held
            checks['pause_freezes_guest_field']=held['field']==before['field'] and held['health']==before['health']
            checks['pause_freezes_audio_render']=size==(out/'audio.wav').stat().st_size and len(drivers())==commands_before
            for choice,label in [(1,'snes'),(2,'md')]:
                row=select()
                for _ in range(4):
                    if latest(trace)['choices'][row['selected']][1]==choice:break
                    key(0x0d)
                snapshots[label+'-draft']=latest(trace);capture_client(hwnd,out/(label+'-draft.png'))
                count=len(drivers());key(0x71);wait(lambda r:not r['menu'] and r['field']<1000)
                after=wait(lambda r:r['field']>=1200 and r['descriptor']==0xc00387 and r['health']>0 and r['macro_index']==r['macro_length'])
                snapshots[label+'-after']=after;capture_client(hwnd,out/(label+'-gameplay.png'))
                checks[label+'_source_applied']=next(c[-1] for c in after['choices'] if c[0]==node)==choice
                checks[label+'_source_persisted']=node+' = '+label in (out/'resources.ini').read_text()
                checks[label+'_difficulty_retained']=after['difficulty']==before['difficulty']
                checks[label+'_other_choices_retained']=effective(after)==effective(before)
                tracks=[int(r['value']) for r in drivers()[count:] if r['selector']=='1']
                checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)
                key(0x7b);wait(lambda r:r['about']==2)
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0;checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source,ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,seed_command=seed_command,command=cmd,snapshots=snapshots,
                own_current_build_seed_and_window=True,actual_os_captures=True,device_audio_tested_separately=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
