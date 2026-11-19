"""New compiled hook sites must preserve the existing native final-life choice."""
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
    base=ROOT/'build/pride-final-scene-compiled-probe';out=base/'native-control';out.mkdir()
    bound(base/'build-report.json');reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(reference)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};commands=[]
    for name,binary in [('public',ROOT/'build/pride-arena-work/tlk_pride_player.exe'),('candidate',base/'player.exe')]:
        folder=out/name;folder.mkdir();cmd=report['commands'][1].copy();cmd[0]=str(binary);cmd.remove('--lle')
        cmd[cmd.index('--load')+1]=str(ROOT/'build/pride-final-continue-fixture/prefatal.state')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='0',TLK_FINAL_FAST_ASSETS='0',
            TLK_FINAL_SCENE_PRESENT='0',TLK_CONTINUE_FAST_RELOAD='0',TLK_CONTINUE_BANK_APPLY='0',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_TRANSITION='0')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
    checks=dict(native_guest_unchanged=hashes(out/'candidate/run.log')==hashes(out/'public/run.log'),
        native_window_unchanged=pixels(out/'candidate/window.png')==pixels(out/'public/window.png'),
        native_pcm_unchanged=pcm(out/'candidate/audio.wav')==pcm(out/'public/audio.wav'))
    paths=[Path(__file__),base/'build-report.json',reference,ROOT/'build/pride-arena-work/tlk_pride_player.exe']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks

if __name__=='__main__':main()
