"""Check that timeout ownership preserves early YES and the native fallback."""
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
    base = ROOT/'build/pride-title-fade2'
    out = base/'controls'
    out.mkdir()
    build = base/'build-report.json'
    bound(build)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    cases = [('yes', ROOT/'build/pride-final-scene-compiled-probe/fresh-compiled', active),
             ('native', ROOT/'build/pride-final-standalone/fallback', clean)]
    commands = []
    checks = {}
    paths = [Path(__file__), build, ROOT/'tools/verify_pride_final_scene_runtime.py']
    for name, prior, env in cases:
        reference = prior/'report.json'
        row = bound(reference)
        cmd = row['command'].copy()
        cmd[0] = str(base/'player.exe')
        folder = out/name
        folder.mkdir()
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        actual = hashes(folder/'run.log')
        checks[name+'/guest'] = len(actual) == 2 and actual == hashes(prior/'run.log')
        checks[name+'/actual_client'] = pixels(folder/'window.png') == pixels(prior/'window.png')
        checks[name+'/full_pcm'] = pcm(folder/'audio.wav') == pcm(prior/'audio.wav')
        paths.append(reference)
        commands.append(cmd)
        print(name, {k: v for k, v in checks.items() if k.startswith(name+'/')}, flush=True)
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  public_player_changed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
