"""Verify Start after the native title menu is visibly ready."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-final-title3'
    out = base/'start-ready'
    out.mkdir()
    reference = base/'verification/report.json'
    row = bound(reference)
    cmd = row['commands'][-1].copy()
    data = bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
    for age in range(500, 504):
        struct.pack_into('<H', data, (3894+age-1)*2, 0)
    for age in range(1000, 1004):
        struct.pack_into('<H', data, (3894+age-1)*2, 0x1000)
    tape = out/'input.tape'
    tape.write_bytes(data)
    cmd[cmd.index('--input')+1] = str(tape)
    for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
        cmd[cmd.index(flag)+1] = str(out/filename)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    env.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
               TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
               TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    with (out/'run.log').open('wb') as log:
        subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    scene = json.loads((out/'scene.json').read_text())['latched_gameplay']
    checks = dict(new_game_plays_pride=scene['descriptor'] == 0x387 and scene['health'] == 4)
    paths = [Path(__file__), reference, base/'build-report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
                  observations=scene, early500_input_not_claimed=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], scene, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
