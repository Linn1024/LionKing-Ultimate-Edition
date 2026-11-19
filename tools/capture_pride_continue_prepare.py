"""Locate remaining Continue preparation delay without changing its behavior."""
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
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-continue-prepare-observer';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json')
    prior=ROOT/'build/pride-continue-fast-reload-probe/capture'
    reference=bound(prior/'report.json');cmd=reference['commands'][1].copy()
    cmd[0]=str(base/'player.exe')
    for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json')]:
        cmd[cmd.index(flag)+1]=str(out/name)
    cmd+=['--wav',str(out/'audio.wav'),'--wav-seconds','120']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',
        TLK_FINAL_SKIP_LOG=str(out/'points.csv'),TLK_CONTINUE_EXIT_LOG=str(out/'exit.csv'),
        TLK_CONTINUE_PREPARE_LOG=str(out/'preparation.csv'))
    with (out/'run.log').open('wb') as log:
        subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=list(csv.DictReader((out/'preparation.csv').open()))
    checks=dict(guest_unchanged=hashes(out/'run.log')==hashes(prior/'fast/run.log'),
        window_unchanged=pixels(out/'window.png')==pixels(prior/'fast/window.png'),
        binary_bound=digest(base/'player.exe')==build['binary_sha256'])
    summary={}
    for row in rows:
        pc=row['pc'];entry=summary.setdefault(pc,dict(count=0,first_age=int(row['age']),last_age=0))
        entry['count']+=1;entry['last_age']=int(row['age'])
    paths=[Path(__file__),base/'build-report.json',prior/'report.json']
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,summary=summary,command=cmd,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,summary,flush=True);assert all(checks.values())


if __name__=='__main__':main()
