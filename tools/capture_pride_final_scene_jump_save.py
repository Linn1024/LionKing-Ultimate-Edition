"""Preserve the accepted held-jump edge across a cold Continue save/load."""
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
    base=ROOT/'build/pride-final-scene-lifecycle-probe';out=base/'jump-save';out.mkdir()
    bound(base/'build-report.json');prior=ROOT/'build/pride-continue-transition-edge-probe/jump-edges'
    reference=prior/'report.json';report=bound(reference);saved=out/'saved.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};commands=[]
    for name,restored,end in [('save',False,433),('resume',True,460)]:
        folder=out/name;folder.mkdir();cmd=report['commands'][0].copy();cmd[0]=str(base/'player.exe')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd[cmd.index('--frames')+1]=str(3894+end)
        if restored:cmd[cmd.index('--load')+1]=str(saved)
        else:cmd+=['--save-at',str(3894+433),str(saved)]
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        if not restored:env['TLK_CONTINUE_BANK_RECORD']=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
    checks=dict(held_jump_guest=hashes(out/'resume/run.log')==hashes(prior/'held/run.log'),
        held_jump_actual_window=pixels(out/'resume/window.png')==pixels(prior/'held/window.png'),
        held_jump_pcm=pcm(out/'save/audio.wav')+pcm(out/'resume/audio.wav')==pcm(prior/'held/audio.wav'))
    source=[Path(__file__),base/'build-report.json',reference]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks

if __name__=='__main__':main()
