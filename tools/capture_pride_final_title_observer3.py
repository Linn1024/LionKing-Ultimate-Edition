"""Observe actual NO/timeout title preparation and verify observer neutrality."""
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
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-final-title-observer3'
    out = base/'capture'
    out.mkdir()
    bound(base/'build-report.json')
    reference = ROOT/'build/pride-final-title3/verification/report.json'
    row = bound(reference)
    sources = [reference]
    cases = [('no', row['commands'][2], reference.parent/'no1000'),
             ('timeout', row['commands'][3], reference.parent/'timeout1600')]
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    checks = {}
    commands = []
    for name, original, reference in cases:
        folder = out/name
        folder.mkdir()
        cmd = original.copy()
        cmd[0] = str(base/'player.exe')
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        env = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                   TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                   TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1',
                   TLK_TITLE_EXIT_LOG=str(folder/'title.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        checks[name+'/guest'] = hashes(folder/'run.log') == hashes(reference/'run.log')
        checks[name+'/client'] = pixels(folder/'window.png') == pixels(reference/'window.png')
        checks[name+'/pcm'] = pcm(folder/'audio.wav') == pcm(reference/'audio.wav')
        commands.append(cmd)
        print(name, {k: v for k, v in checks.items() if k.startswith(name+'/')}, flush=True)
    paths = [Path(__file__), base/'build-report.json', *sources]
    report = dict(result='NEUTRAL' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
