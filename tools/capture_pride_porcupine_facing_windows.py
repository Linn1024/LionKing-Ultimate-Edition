"""Inspect both ordinary attack facings through genuine saves and own windows."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    source=ROOT/'build/pride-porcupine-lifetimes/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=ROOT/'build/pride-porcupine-facing-windows';out.mkdir()
    rows=list(csv.DictReader((source.parent/'mixed-aot/actors.csv').open()))
    reference=source.parent/'mixed-aot/run.log'
    samples={int(f):(picture,ram) for f,picture,ram in re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',reference.read_text())}
    template=prior['commands']['mixed-aot'].copy();commands={};checks={};cases={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    USER32.SetProcessDPIAware()
    for facing in (0,1):
        entry=next(r for r in rows if r['action']=='c15b87' and r['facing']==str(facing))
        field=int(entry['field']);seed=out/f'face{facing}-seed';seed.mkdir();cmd=template.copy()
        cmd[0]=str(ROOT/'build/pride-sprite-fresh44/player.exe')
        for flag,value in [('--frames',field),('--hash-at',field),('--dump-window',seed/'window.png'),
                            ('--dump-scene',seed/'scene.json'),('--wav',seed/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=seed/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        state=seed/'saved.state';cmd+=['--save-at',str(field),str(state)]
        commands[f'face{facing}-seed']=cmd
        with (seed/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_SOFT_TREE_LOG=str(seed/'tree.jsonl')),
                              stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[f'face{facing}_seed_exit']=rc==0 and state.exists()
        sample=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(seed/'run.log').read_text())
        checks[f'face{facing}_seed_exact_reference']=len(sample)==1 and tuple(sample[0][1:])==samples[field]
        row=latest(seed/'tree.jsonl');assert row['field']==field
        original_tape=Path(cmd[cmd.index('--input-polled')+1]);folder=out/f'face{facing}-window';folder.mkdir()
        tape=folder/'suffix.tape';tape.write_bytes(original_tape.read_bytes()[row['poll_index']*2:])
        play=template.copy();play.remove('--no-pace')
        for flag,value in [('--frames',field+240),('--input-polled',tape),('--hash-at',field+1),
                            ('--dump-window',folder/'final.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:play[play.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes((seed/name).read_bytes());play[play.index(flag)+1]=str(p)
        play+=['--load',str(state)];commands[f'face{facing}-window']=play
        state_hash=digest(state);profile_hash=digest(folder/'resources.ini');trace=folder/'tree.jsonl'
        env=dict(clean,TLK_SOFT_TREE_LOG=str(trace),TLK_PORCUPINE_LIFETIME_LOG=str(folder/'actors.csv'))
        hwnd=None;observed=None
        with (folder/'run.log').open('wb') as log:
            proc=subprocess.Popen(play,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                deadline=time.monotonic()+30
                while proc.poll() is None and time.monotonic()<deadline:
                    hwnd=window_for(proc.pid);current=latest(trace)
                    if hwnd and current and current['field']>=field+1:
                        actor_rows=list(csv.DictReader((folder/'actors.csv').open()))
                        found=[r for r in actor_rows if r['actor']==entry['actor']]
                        if found:observed=found[-1];break
                    time.sleep(.01)
                assert hwnd and observed
                capture_client(hwnd,folder/'gameplay.png')
                checks[f'face{facing}_live_active_attack']=observed['action']=='c15b87' and observed['facing']==str(facing) and int(observed['wait'])>0
                checks[f'face{facing}_actual_capture_early']=field<int(observed['field'])<=field+10
            finally:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        checks[f'face{facing}_clean_exit']=proc.returncode==0
        checks[f'face{facing}_state_profile_preserved']=digest(state)==state_hash and digest(folder/'resources.ini')==profile_hash
        checks[f'face{facing}_genuine_state_loaded']='loaded_state=' in (folder/'run.log').read_text()
        cases[str(facing)]=dict(entry=entry,observed=observed,process=proc.pid)
        print('facing',facing,'seed',field,'observed',observed['field'],flush=True)
    paths=[Path(__file__),source,reference]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,cases=cases,
                ordinary_poweron_seeds=True,genuine_cold_loads=True,operating_only_own_child_windows=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
