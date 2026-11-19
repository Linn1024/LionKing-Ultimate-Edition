"""Actual host pause, turbo and saved-slot load with paced queue telemetry."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import time

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-audio-prime28';build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-restart-difficulty-fixtures/report.json';fixtures=bound(source)
    out=base/'queue-ui';out.mkdir();checks={};snapshots={};hwnd=None
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\naudio = 1\n')
    cmd=fixtures['commands']['md-normal'].copy();cmd[0]=str(base/'player.exe')
    for flag in ('--save-at','--input'):
        if flag in cmd:i=cmd.index(flag);del cmd[i:i+(3 if flag=='--save-at' else 2)]
    for flag in ('--no-audio','--no-pace'):
        if flag in cmd:cmd.remove(flag)
    for flag,value in [('--config',config),('--frames',15000),('--dump-window',out/'window.png'),
                       ('--dump-scene',out/'scene.json'),('--wav',out/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    cmd+=['--load',str(source.parent/'md-normal/saved.state')]
    tree=out/'tree.jsonl';queue=out/'queue.csv'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(TLK_FINAL_MD_ART='1',SDL_AUDIO_DRIVER='wasapi',TLK_SOFT_TREE_LOG=str(tree),TLK_AUDIO_QUEUE_TRACE=str(queue))
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate,timeout=15):
            end=time.monotonic()+timeout
            while proc.poll() is None and time.monotonic()<end:
                row=latest(tree)
                if row and predicate(row):return row
                time.sleep(.01)
            raise AssertionError(('UI timeout',proc.poll(),latest(tree)))
        def post(vk,down):
            scan=USER32.MapVirtualKeyW(vk,0)
            assert USER32.PostMessageW(hwnd,0x100 if down else 0x101,vk,1+(scan<<16)+(0 if down else 0xc0000000))
        def key(vk):post(vk,True);post(vk,False);time.sleep(.06)
        try:
            USER32.SetProcessDPIAware();end=time.monotonic()+15
            while not hwnd and time.monotonic()<end and proc.poll() is None:
                hwnd=window_for(proc.pid);time.sleep(.01)
            assert hwnd
            initial=wait(lambda r:r['field']>=2020);snapshots['initial']=initial
            key(0x70);checks['saved_slot']=(out/'tlk_slot1.state').exists()
            key(0x09);paused=wait(lambda r:r['menu']==1);snapshots['paused']=paused
            capture_client(hwnd,out/'paused.png');time.sleep(.25)
            checks['host_pause_stops_guest']=latest(tree)['field']==paused['field']
            key(0x09);returned=wait(lambda r:not r['menu'] and r['field']>=paused['field']+20)
            snapshots['resumed']=returned
            post(0xc0,True);fast=wait(lambda r:r['field']>=returned['field']+80);post(0xc0,False)
            snapshots['turbo']=fast;normal=wait(lambda r:r['field']>=fast['field']+20)
            key(0x74);loaded=wait(lambda r:r['field']>=normal['field']+20)
            snapshots['loaded']=loaded;capture_client(hwnd,out/'loaded.png')
            checks['still_pride']=loaded['level']==0 and loaded['descriptor']==0xc00387
            checks['difficulty_preserved']=loaded['difficulty']==1
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['exit']=proc.returncode==0
    log=(out/'run.log').read_text();stats=re.search(r'audio_underruns=(\d+) late_resyncs=(\d+)',log)
    with queue.open() as stream:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(stream)]
    checks['no_queue_underruns']=stats is not None and int(stats[1])==0
    checks['no_missing_requests']=rows[-1]['missing_calls']==0
    paused_starts=[r['frame'] for i,r in enumerate(rows) if r['paused'] and (i==0 or not rows[i-1]['paused'])]
    checks['four_prime_episodes']=len(paused_starts)>=4
    checks['every_prime_resumes']=sum(not r['paused'] and rows[i-1]['paused'] for i,r in enumerate(rows) if i)==len(paused_starts)
    observations=dict(paused_starts=paused_starts,last_row=rows[-1],underruns=int(stats[1]) if stats else None)
    paths=[Path(__file__),build,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,snapshots=snapshots,command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),observations,[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
