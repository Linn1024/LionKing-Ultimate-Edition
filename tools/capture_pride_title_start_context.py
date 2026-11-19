"""Compare new-game loading with retained versus cleared final-scene context."""
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
from verify_windows import hashes, pixels
from verify_pride_final_scene_runtime import pcm


def main():
    out = ROOT/'build/pride-title-start-context'
    out.mkdir()
    reference = ROOT/'build/pride-final-title3/verification/report.json'
    row = bound(reference)
    prototype = row['commands'][2]
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    saved = out/'title.state'
    commands = []
    def run(name, load=None):
        folder = out/name
        folder.mkdir()
        cmd = prototype.copy()
        cmd[cmd.index('--frames')+1] = str(4894 if name == 'save' else 5694)
        if load:
            cmd[cmd.index('--load')+1] = str(load)
            data = bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
            data += bytes(max(0, 5694*2-len(data)))
            for field in range(4994, 4998):
                struct.pack_into('<H', data, (field-1)*2, 0x1000)
            tape = folder/'input.tape'
            tape.write_bytes(data)
            cmd[cmd.index('--input')+1] = str(tape)
        else:
            cmd += ['--save-at', '4894', str(saved)]
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        env = dict(active, TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
    run('save')
    raw = saved.read_bytes()
    native_size = struct.unpack_from('<I', raw, 20)[0]
    native = out/'native-title.state'
    native.write_bytes(raw[96:96+native_size])
    run('retained', saved)
    run('cleared', native)
    events = lambda name: [r for r in csv.DictReader((out/name/'exit.csv').open()) if r['kind'] == 'fast']
    observations = dict(retained_fast_events=len(events('retained')), cleared_fast_events=len(events('cleared')),
                        guest_equal=hashes(out/'retained/run.log') == hashes(out/'cleared/run.log'),
                        client_equal=pixels(out/'retained/window.png') == pixels(out/'cleared/window.png'),
                        pcm_equal=pcm(out/'retained/audio.wav') == pcm(out/'cleared/audio.wav'))
    paths = [Path(__file__), reference, ROOT/'build/pride-final-title3/build-report.json']
    report = dict(result='OBSERVED', observations=observations, commands=commands,
                  native_guest_bytes_unmodified=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(observations, flush=True)


if __name__ == '__main__':
    main()
