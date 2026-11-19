"""Load an earlier private/native save while Continue is already active."""
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
    base=ROOT/'build/pride-final-scene-save-probe';out=base/'live-loads';out.mkdir()
    reference=base/'capture/report.json';report=bound(reference)
    prior=ROOT/'build/pride-continue-transition-edge-probe/pixel-checks/600'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];checks={}
    paths=[('private100',base/'capture/100/saved.state'),('legacy',ROOT/'build/pride-final-continue-fixture/prefatal.state')]
    for name,path in paths:
        folder=out/name;folder.mkdir();cmd=report['commands'][3].copy()
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd+=['--load-at',str(3894+420),str(path)]
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
        checks[name+'/guest']=hashes(folder/'run.log')==hashes(prior/'run.log')
        checks[name+'/actual_window']=pixels(folder/'window.png')==pixels(prior/'window.png')
        direct=pcm(prior/'audio.wav');start=len(pcm(base/'capture/300/save/audio.wav'));end=len(pcm(base/'capture/420/save/audio.wav'))
        restart=len(pcm(base/'capture/100/save/audio.wav')) if name=='private100' else 0
        checks[name+'/pcm']=pcm(folder/'audio.wav')==direct[start:end]+direct[restart:]
        print(name,{k:v for k,v in checks.items() if k.startswith(name+'/')},flush=True)
    source=[Path(__file__),reference,*(p for n,p in paths)]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
