"""Observe NO/timeout in the maintained private final-scene Windows player."""
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
    out = ROOT/'build/pride-final-menu-exits-player'
    out.mkdir()
    base = ROOT/'build/pride-final-scene-runtime'
    bound(base/'build-report.json')
    source = ROOT/'build/pride-final-scene-compiled-probe/native-control/report.json'
    prototype = bound(source)['commands'][0]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    env.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
               TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
               TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    observations = {}
    commands = []
    fatal = 3894
    for name in ('no', 'timeout'):
        data = bytearray(Path(prototype[prototype.index('--input')+1]).read_bytes()[:(fatal-1)*2])
        for age in range(1601):
            pad = 0
            if name == 'no':
                if 130 <= age <= 133:
                    pad = 0x100
                elif 140 <= age <= 143:
                    pad = 0x8000
            data += struct.pack('<H', pad)
        tape = out/(name+'.tape')
        tape.write_bytes(data)
        for end in (300, 1000, 1600):
            folder = out/f'{name}-{end}'
            folder.mkdir()
            cmd = prototype.copy()
            cmd[0] = str(base/'player.exe')
            cmd[cmd.index('--frames')+1] = str(fatal+end)
            cmd[cmd.index('--input')+1] = str(tape)
            for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
                cmd[cmd.index(flag)+1] = str(folder/filename)
            with (folder/'run.log').open('wb') as log:
                subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
            observations[f'{name}-{end}'] = json.loads((folder/'scene.json').read_text())['latched_gameplay']
            commands.append(cmd)
            print(name, end, observations[f'{name}-{end}'], flush=True)
    paths = [Path(__file__), source, base/'build-report.json']
    report = dict(result='OBSERVED', observations=observations, commands=commands,
                  independent_menu_art_or_audio_verified=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
