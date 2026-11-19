"""Check actual F12 restarts retain an ordinary selected difficulty after cold loads."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-pickup-flight34');parser.add_argument('--only');parser.add_argument('--lle',action='store_true');args=parser.parse_args()
    base=ROOT/args.player;bound(base/'build-report.json')
    source=ROOT/'build/pride-pickup-flight34/wide-flight-view/report.json';fixture=bound(source)
    out=base/('flight-ui-lle' if args.lle else 'flight-ui');out.mkdir();checks={};commands={};snapshots={}
    cases=['md-easy']
    for case in cases:
        folder=out/case;folder.mkdir();expected={'easy':0,'normal':1,'difficult':2}[case.split('-')[1]]
        seed=source.parent/'saved.state';profile=folder/'resources.ini';profile.write_bytes((source.parent/'resources.ini').read_bytes())
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        trace=folder/'tree.jsonl';node='gameplay.levels.pride_lands.pickup_flight';cmd=fixture['command'].copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        if '--no-pace' in cmd:cmd.remove('--no-pace')
        if '--input-polled' in cmd:i=cmd.index('--input-polled');del cmd[i:i+2]
        if args.lle:cmd.append('--lle')
        for flag,value in [('--frames',15000),('--config',config),('--resource-profile',profile),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--load',str(seed)]
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(TLK_SOFT_TREE_LOG=str(trace));commands[case]=cmd;hwnd=None
        with (folder/'run.log').open('wb') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            def wait(predicate,timeout=30):
                end=time.monotonic()+timeout
                while proc.poll() is None and time.monotonic()<end:
                    row=latest(trace)
                    if row and predicate(row):return row
                    time.sleep(.01)
                raise AssertionError((case,'UI timeout',proc.poll(),latest(trace)))
            def key(vk):
                scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
                assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
                assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
            try:
                USER32.SetProcessDPIAware();end=time.monotonic()+15
                while not hwnd and time.monotonic()<end and proc.poll() is None:hwnd=window_for(proc.pid);time.sleep(.01)
                assert hwnd;before=wait(lambda r:r['field']>=1600 and r['descriptor']==0xc00387)
                snapshots[case+'-cold']=before;checks[case+'_cold_difficulty']=before['difficulty']==expected
                checks[case+'_cold_budget']=before['lives']==8 and before['health']>0
                targets=(2,1) if case.startswith('snes-') else (1,2)
                for target in targets:
                    label=case+'-to-'+('md' if target==2 else 'snes');key(0x7b);wait(lambda r:r['about']==2,5);key(0x24)
                    for _ in range(180):
                        row=latest(trace);selected=row['choices'][row['selected']][0]
                        if selected==node:break
                        if selected=='game' or node.startswith(selected+'.'):key(0x27)
                        key(0x28)
                    assert selected==node
                    for _ in range(3):
                        if latest(trace)['choices'][row['selected']][1]==target:break
                        key(0x0d)
                    snapshots[label+'-before']=latest(trace);key(0x71)
                    wait(lambda r:not r['menu'] and r['field']<1000,5)
                    after=wait(lambda r:r['field']>=2000 and r['descriptor']==0xc00387)
                    snapshots[label+'-after']=after;capture_client(hwnd,folder/(label+'.png'))
                    checks[label+'_difficulty']=after['difficulty']==expected
                    checks[label+'_budget']=after['lives']=={0:8,1:2,2:0}[expected] and after['health']==4
                    checks[label+'_persisted']=node+' = '+('md' if target==2 else 'snes') in profile.read_text()
                    checks[label+'_macro_finished']=after['macro_index']==after['macro_length']
                    key(0x70);checks[label+'_save_exists']=(folder/'tlk_slot1.state').exists()
                    print(label,{k:after[k] for k in ('difficulty','lives','health','macro_length')},flush=True)
            finally:
                if proc.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        checks[case+'_exit']=proc.returncode==0
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,snapshots=snapshots,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
