"""Compare both execution configurations through actual title appearance."""
import json
from pathlib import Path
import os
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes, pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-title-fade2'
    out = base/'title-modes'
    out.mkdir()
    reference = base/'verification/report.json'
    row = bound(reference)
    active = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    checks = {}
    commands = []
    for name in ('no279','timeout984'):
        prior = reference.parent/name
        cmd = next(c.copy() for c in row['commands'] if Path(c[c.index('--dump-window')+1]) == prior/'window.png')
        folder = out/name
        folder.mkdir()
        cmd += ['--lle']
        for flag, filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
        checks[name+'/guest'] = len(hashes(folder/'run.log')) == 2 and hashes(folder/'run.log') == hashes(prior/'run.log')
        checks[name+'/client'] = pixels(folder/'window.png') == pixels(prior/'window.png')
        checks[name+'/pcm'] = pcm(folder/'audio.wav') == pcm(prior/'audio.wav')
    paths = [Path(__file__), base/'build-report.json', reference]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
