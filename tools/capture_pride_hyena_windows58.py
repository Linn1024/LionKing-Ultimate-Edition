"""Inspect current Normal/Difficult mixed boss victories through own OS windows."""
from concurrent.futures import ThreadPoolExecutor
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
    source=ROOT/'build/pride-hyena-mixtures58/report.json';prior=bound(source)
    planpath=ROOT/'build/pride-hyena-mixed-plan58/report.json';plan=bound(planpath);assert plan['result']=='PASS'
    out=ROOT/'build/pride-hyena-windows58';out.mkdir();checks={};commands={};snapshots={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware()
    def run(difficulty):
        folder=out/difficulty;folder.mkdir();cmd=prior['commands'][difficulty+'-mixed-aot'].copy()
        cmd[0]=str(ROOT/'dist/installed-preview53/LionKing.exe')
        for flag,count in [('--save-at',3),('--hash-at',2),('--dump-window',2)]:i=cmd.index(flag);del cmd[i:i+count]
        cmd.remove('--no-pace')
        if difficulty=='normal':
            seed=source.parent/'normal-mixed-aot/current.state';start=4275;capture=4320;end=4330
            tree=[json.loads(r) for r in (source.parent/'normal-mixed-aot/tree.jsonl').read_text().splitlines()]
            row=next(r for r in tree if r['field']==start)
            tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes()[row['poll_index']*2:]
        else:
            seed=planpath.parent/'fresh-aot/current.state';start=plan['frames'];capture=start+2;end=start+20;tape=bytes(4096)
        tail=folder/'tail.polled.tape';tail.write_bytes(tape);cmd[cmd.index('--input-polled')+1]=str(tail)
        cmd[cmd.index('--frames')+1]=str(end);cmd+=['--load',str(seed)]
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            path=folder/name;path.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(path)
        for flag,name in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        commands[difficulty]=cmd;trace=folder/'tree.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace));hwnd=None
        with (folder/'run.log').open('wb') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                deadline=time.monotonic()+30
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(trace)
                    if row and row['field']>=capture:
                        hwnd=window_for(proc.pid)
                        if hwnd:break
                    time.sleep(.002)
                assert hwnd,('victory window missing',difficulty,latest(trace))
                before=latest(trace);capture_client(hwnd,folder/'victory.png');after=latest(trace)
                snapshots[difficulty]=dict(before=before,after=after)
                checks[difficulty+'_captured_current_victory_interval']=capture<=before['field']<=after['field']<=end
                checks[difficulty+'_correct_difficulty']=before['difficulty']==(1 if difficulty=='normal' else 2)
                checks[difficulty+'_alive_in_pride_arena']=before['health']>0 and before['level']==0 and before['descriptor']==0xc0080d
                selected=lambda key:next(c for c in before['choices'] if c[0]==key)[-1]
                checks[difficulty+'_md_hyena_frames_and_sound_selected']=selected('graphics.sprites.enemies.hyenas.frames')==2 and selected('audio.effects.world.hyena_hurt')==2
                proc.wait(timeout=30);checks[difficulty+'_clean_exit']=proc.returncode==0
            finally:
                if proc.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        scene=json.loads((folder/'scene.json').read_text())
        checks[difficulty+'_retains_owned_dead_hyena']=any(p['actor_descriptor']==0xc58c68 and p['actor_owner']==p['object'] and p['actor_action']==0xc147f7 for p in scene['pieces'])
        print(difficulty,'captured',before['field'],flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,('normal','hard')))
    paths=[Path(__file__),source,planpath,ROOT/'dist/installed-preview53/package-report.json',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,snapshots=snapshots,
                operates_only_own_child_windows=True,current_build_states_only=True,cross_build_save_compatibility_tested=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
