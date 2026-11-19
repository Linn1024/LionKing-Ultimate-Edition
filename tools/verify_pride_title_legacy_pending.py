"""Resume older pending/consumed title returns before starting a new game."""
import csv
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
    base = ROOT/'build/pride-title-lifecycle'
    out = base/'legacy-pending'
    out.mkdir()
    reference = ROOT/'build/pride-title-start-context/report.json'
    prototype = bound(reference)['commands'][1]
    old = ROOT/'build/pride-final-title3/verification/report.json'
    bound(old)
    control = reference.parent/'cleared'
    active = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    commands = []
    checks = {}
    for age in (180, 240, 360):
        folder = out/str(age)
        folder.mkdir()
        cmd = prototype.copy()
        cmd[0] = str(base/'player.exe')
        cmd[cmd.index('--load')+1] = str(old.parent/f'save{age}/saved.state')
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=dict(active, TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv')),
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
        rows = list(csv.DictReader((folder/'exit.csv').open()))
        checks[f'{age}/ordinary_new_game'] = not any(r['kind'] == 'fast' for r in rows)
        checks[f'{age}/guest'] = len(hashes(folder/'run.log')) == 2 and hashes(folder/'run.log') == hashes(control/'run.log')
        checks[f'{age}/client'] = pixels(folder/'window.png') == pixels(control/'window.png')
        audio = pcm(control/'audio.wav')
        checks[f'{age}/shared_pcm_tail'] = pcm(folder/'audio.wav')[-len(audio):] == audio
        print(age, {k: v for k, v in checks.items() if k.startswith(str(age)+'/')}, flush=True)
    paths = [Path(__file__), base/'build-report.json', reference, old]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
