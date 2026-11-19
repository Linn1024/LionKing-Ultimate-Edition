"""Reset an owned resource-selected final episode through the real machine API."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-final-resource2';out=base/'reset';out.mkdir()
    build=base/'build-report.json';bound(build)
    source=base/'lifecycle/report.json';previous=bound(source)
    cmd=previous['commands']['cold-menu'].copy();cmd[cmd.index('--frames')+1]='3802'
    for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    cmd+=['--save-at','3802',str(out/'saved.state')]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_MACHINE_RESET_AT='3801',TLK_FINAL_RESET_LOG=str(out/'final-reset.json'),TLK_PRIDE_DIAGNOSTICS=str(out))
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    reset=json.loads((out/'final-reset.json').read_text())
    checks=dict(exit=result.returncode==0,owned_episode_before_reset=reset['before_entry']==3793,
        episode_cleared=reset['after_entry']==0,level_canvas_cleared=reset['after_level_ready']==0,
        bank_cleared=reset['after_bank_ready']==0,frontend_clock_reset=reset['frontend_frame']==0,
        after_reset_save_exists=(out/'saved.state').is_file())
    paths=[Path(__file__),build,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,reset=reset,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
