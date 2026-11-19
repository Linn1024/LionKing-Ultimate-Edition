"""Observe a fresh final death after NO, title and a real new-game Start."""
import csv
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
    out = ROOT/'build/pride-title-second-game-after'
    out.mkdir()
    reference = ROOT/'build/pride-final-title3/start-ready/report.json'
    row = bound(reference)
    cmd = row['command'].copy()
    cmd[0] = str(ROOT/'build/pride-title-lifecycle/player.exe')
    data = bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
    first = len(data)//2+1
    for field in range(first, 10501):
        data += struct.pack('<H', 0x100 if ((field-first)//240)%2 == 0 else 0x200)
    tape = out/'input.tape'
    tape.write_bytes(data)
    cmd[cmd.index('--frames')+1] = '10500'
    cmd[cmd.index('--input')+1] = str(tape)
    for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
        cmd[cmd.index(flag)+1] = str(out/filename)
    saved = out/'saved.state'
    cmd += ['--save-at', '10500', str(saved)]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    env.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
               TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
               TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1',
               TLK_FINAL_SKIP_LOG=str(out/'points.csv'))
    with (out/'run.log').open('wb') as log:
        subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
    points = list(csv.DictReader((out/'points.csv').open()))
    fatal = [int(p['field']) for p in points if p['pc'] == 'c089b9' and p['spares'] == '0']
    raw = saved.read_bytes()
    native = struct.unpack_from('<I', raw, 20)[0]
    entry = struct.unpack_from('<I', raw, 96+native+100)[0]
    observations = dict(final_entries=fatal, saved_owned_entry=entry,
                        scene=json.loads((out/'scene.json').read_text())['latched_gameplay'])
    paths = [Path(__file__), reference, ROOT/'build/pride-title-lifecycle/build-report.json']
    report = dict(result='OBSERVED', command=cmd, observations=observations,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(observations, flush=True)


if __name__ == '__main__':
    main()
