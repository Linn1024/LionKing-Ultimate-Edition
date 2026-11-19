"""Ensure an uncached YES fallback retires the live-menu snapshot before reload."""
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
    base = ROOT/'build/pride-title-fade2'
    out = base/'cold-yes'
    out.mkdir()
    reference = ROOT/'build/pride-final-scene-compiled-probe/fresh-compiled/report.json'
    template = bound(reference)['command']
    active = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    commands = []
    saved = out/'saved.state'
    for name, end in [('direct',600),('save',400),('resume',600)]:
        folder = out/name
        folder.mkdir()
        cmd = template.copy()
        cmd[0] = str(base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(3894+end)
        cmd += ['--load', str(saved if name == 'resume' else ROOT/'build/pride-final-continue-fixture/prefatal.state')]
        if name == 'save':
            cmd += ['--save-at', '4294', str(saved)]
        for flag, filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
    raw = saved.read_bytes()
    native = struct.unpack_from('<I', raw, 20)[0]
    record = raw[96+native:]
    flags, reload = struct.unpack_from('<II', record, 108)
    menu, fade = struct.unpack_from('<II', record, 160)
    scene = json.loads((out/'resume/scene.json').read_text())['latched_gameplay']
    checks = dict(no_stale_menu_snapshot=not(flags&256) and menu == fade == 0 and reload != 0,
                  cold_resume_guest=hashes(out/'resume/run.log') == hashes(out/'direct/run.log'),
                  cold_resume_client=pixels(out/'resume/window.png') == pixels(out/'direct/window.png'),
                  cold_resume_pcm=pcm(out/'save/audio.wav')+pcm(out/'resume/audio.wav') == pcm(out/'direct/audio.wav'),
                  returned_to_pride=scene['descriptor'] == 0x387 and scene['health'] == 4)
    paths = [Path(__file__), reference, base/'build-report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
