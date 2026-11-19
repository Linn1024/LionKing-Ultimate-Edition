"""Reset from an active incoming fade and compare with a real fresh boot."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-final-scene-lifecycle-probe';out=base/'reset';out.mkdir()
    build=bound(base/'build-report.json');prior=ROOT/'build/pride-continue-bank-ready-probe/capture'
    reference=bound(prior/'report.json');saved=ROOT/'build/pride-final-scene-save-probe/capture/420/saved.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];checks={}
    for name,reset in [('fresh',False),('reset',True)]:
        folder=out/name;folder.mkdir();cmd=reference['commands'][0].copy();cmd[0]=str(base/'player.exe')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        if reset:cmd+=['--load',str(saved)]
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        if reset:env.update(TLK_MACHINE_RESET_AT=str(3894+420),TLK_MACHINE_RESET_KIND='reset',TLK_FINAL_RESET_LOG=str(folder/'reset.json'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd);print(name,'completed',flush=True)
    event=json.loads((out/'reset/reset.json').read_text())
    checks['active_state_before_reset']=event['before_entry']==3894 and event['before_level_ready']==1 and event['before_bank_ready']==1
    checks['state_cache_time_cleared']=event['after_entry']==0 and event['after_level_ready']==0 and event['after_bank_ready']==0 and event['frontend_frame']==0
    checks['fresh_guest_matches_preceding']=hashes(out/'fresh/run.log')==hashes(prior/'boot/run.log')
    checks['reset_guest_matches_fresh']=hashes(out/'reset/run.log')==hashes(out/'fresh/run.log')
    checks['reset_actual_window_matches_fresh']=pixels(out/'reset/window.png')==pixels(out/'fresh/window.png')
    source=[Path(__file__),base/'build-report.json',prior/'report.json',saved]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,event=event,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,event,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
