"""Save during Continue phases and resume each in a fresh Windows process."""
import json
import os
from pathlib import Path
import subprocess
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def pcm(path):
    with wave.open(str(path),'rb') as f:return f.readframes(f.getnframes())


def main():
    base=ROOT/'build/pride-final-scene-compiled-probe';out=base/'save-checks';out.mkdir()
    build=bound(base/'build-report.json')
    prior=ROOT/'build/pride-continue-transition-edge-probe/pixel-checks'
    reference=bound(prior/'report.json');prototype=ROOT/'build/pride-continue-bank-ready-probe/capture'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];checks={};observations={}
    for age in (100,300,407,420,433):
        target=out/str(age);target.mkdir();saved=target/'saved.state'
        for name,restored,end in [('save',False,age),('resume',True,600)]:
            folder=target/name;folder.mkdir();cmd=reference['commands'][1].copy();cmd[0]=str(base/'player.exe');cmd.remove('--lle')
            for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
            cmd[cmd.index('--frames')+1]=str(3894+end)
            if restored:cmd[cmd.index('--load')+1]=str(saved)
            else:cmd+=['--save-at',str(3894+age),str(saved)]
            env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
                TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
                TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
                TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
            if not restored:env['TLK_CONTINUE_BANK_RECORD']=str(prototype/'boot/bank.record')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                    creationflags=subprocess.CREATE_NO_WINDOW)
            commands.append(cmd)
        checks[f'{age}/private_single_file']=saved.read_bytes()[:8]==b'TLKFSV01'
        checks[f'{age}/guest_endpoint']=hashes(target/'resume/run.log')==hashes(prior/'600/run.log')
        checks[f'{age}/actual_window']=pixels(target/'resume/window.png')==pixels(prior/'600/window.png')
        checks[f'{age}/pcm_continuation']=pcm(target/'save/audio.wav')+pcm(target/'resume/audio.wav')==pcm(prior/'600/audio.wav')
        observations[str(age)]=dict(bytes=saved.stat().st_size,checks={k:v for k,v in checks.items() if k.startswith(str(age)+'/')})
        print(age,observations[str(age)],flush=True)
    paths=[Path(__file__),base/'build-report.json',prior/'report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
