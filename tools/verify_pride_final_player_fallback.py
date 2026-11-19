"""Verify the maintained final-scene component remains inert by default."""
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
    base = ROOT/'build/pride-final-standalone'
    out = base/'fallback'
    out.mkdir()
    build = base/'build-report.json'
    bound(build)
    reference = ROOT/'build/pride-final-scene-compiled-probe/native-control'
    old = bound(reference/'report.json')
    cmd = old['commands'][0].copy()
    cmd[0] = str(base/'player.exe')
    for flag, name in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
        cmd[cmd.index(flag)+1] = str(out/name)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    with (out/'run.log').open('wb') as log:
        subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    checks = dict(native_guest_unchanged=hashes(out/'run.log') == hashes(reference/'public/run.log'),
                  native_client_unchanged=pixels(out/'window.png') == pixels(reference/'public/window.png'),
                  native_pcm_unchanged=pcm(out/'audio.wav') == pcm(reference/'public/audio.wav'),
                  no_research_sidecars=not any(out.glob('*.csv')) and not any(out.glob('*.bin')) and not any(out.glob('*.record')))
    paths = [Path(__file__), build, reference/'report.json', ROOT/'tools/verify_pride_final_scene_runtime.py']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
