"""Capture native Continue reload payloads and verify observer neutrality."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes, pixels


def main():
    base = ROOT/'build/pride-continue-reload-probe'
    build = bound(base/'build-report.json')
    prior = ROOT/'build/pride-continue-exit-observation2'
    original = bound(prior/'report.json')
    out = base/'capture'; out.mkdir()
    cmd = original['commands'][-1].copy()
    cmd[0] = str(base/'player.exe')
    for flag, name in [('--dump-window','window.png'), ('--dump-scene','scene.json')]:
        cmd[cmd.index(flag)+1] = str(out/name)
    env = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    env.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1', TLK_FINAL_SKIP_LOG=str(out/'points.csv'),
        TLK_CONTINUE_EXIT_LOG=str(out/'exit.csv'), TLK_CONTINUE_RELOAD_DIR=str(out))
    with (out/'run.log').open('wb') as log:
        subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=240, creationflags=subprocess.CREATE_NO_WINDOW)
    reference = prior/'native/600'
    checks = dict(guest_unchanged=hashes(out/'run.log') == hashes(reference/'run.log'),
                  window_unchanged=pixels(out/'window.png') == pixels(reference/'window.png'),
                  binary_bound=digest(base/'player.exe') == build['binary_sha256'])
    paths = [Path(__file__), base/'build-report.json', prior/'report.json']
    report = dict(result='OBSERVED' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
        public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__': main()
