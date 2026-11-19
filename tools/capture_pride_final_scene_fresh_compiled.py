"""Observe the existing final-scene prototype in normal compiled execution."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    base=ROOT/'build/pride-final-scene-compiled-probe';out=base/'fresh-compiled';out.mkdir()
    bound(base/'build-report.json');ref=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(ref)
    cmd=report['commands'][1].copy();cmd[0]=str(base/'player.exe');cmd.remove('--lle')
    i=cmd.index('--load');del cmd[i:i+2]
    for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
        TLK_CONTINUE_BANK_DIR=str(out),
        TLK_FINAL_SKIP_LOG=str(out/'points.csv'),TLK_CONTINUE_TRANSITION='1',
        TLK_CONTINUE_TRANSITION_LOG=str(out/'transition.csv'))
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,
            creationflags=subprocess.CREATE_NO_WINDOW)
    rows=list(csv.DictReader((out/'transition.csv').open())) if (out/'transition.csv').exists() else []
    observations=dict(exit_code=run.returncode,owned_transition_fields=len(rows))
    source=[Path(__file__),base/'build-report.json',ref]
    result=dict(result='OBSERVED',observations=observations,command=cmd,compiled_support_established=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(observations,flush=True)

if __name__=='__main__':main()
