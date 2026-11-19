"""Verify the next final scene after an ordinary title/new-game sequence."""
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
    base = ROOT/'build/pride-title-lifecycle'
    out = base/'second-final'
    out.mkdir()
    reference = ROOT/'build/pride-title-second-game-after/report.json'
    row = bound(reference)
    entries = row['observations']['final_entries']
    assert len(entries) == 2 and entries[1] > 5500, entries
    fatal = entries[1]
    active = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active.update(TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    saved = out/'scene100.state'
    commands = []
    observations = {}
    for name, age in [('save100', 100), ('direct144', 144), ('resume144', 144), ('interpreted144', 144)]:
        folder = out/name
        folder.mkdir()
        cmd = row['command'].copy()
        cmd[cmd.index('--frames')+1] = str(fatal+age)
        i = cmd.index('--save-at')
        del cmd[i:i+3]
        if name == 'save100':
            cmd += ['--save-at', str(fatal+age), str(saved)]
        elif name == 'resume144':
            cmd[cmd.index('--load')+1] = str(saved)
        elif name == 'interpreted144':
            cmd += ['--lle']
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
        observations[name] = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        commands.append(cmd)
        print(name, observations[name], flush=True)
    raw = saved.read_bytes()
    native = struct.unpack_from('<I', raw, 20)[0]
    field, entry, age = struct.unpack_from('<III', raw, 96+native+96)
    checks = dict(first_episode_completed=row['observations']['saved_owned_entry'] == 0,
                  fresh_second_entry=entry == fatal and field == fatal+100 and age == 100,
                  second_menu_visible=observations['save100']['descriptor'] == 0x57b and
                      sum(p != (0, 0, 0) for p in pixels(out/'save100/window.png')[2]) > 0,
                  held_menu_usable=observations['direct144']['descriptor'] == 0x57b)
    for name in ('resume144', 'interpreted144'):
        checks[name+'/guest'] = len(hashes(out/name/'run.log')) == 2 and hashes(out/name/'run.log') == hashes(out/'direct144/run.log')
        checks[name+'/client'] = pixels(out/name/'window.png') == pixels(out/'direct144/window.png')
    checks['cold_pcm'] = pcm(out/'save100/audio.wav')+pcm(out/'resume144/audio.wav') == pcm(out/'direct144/audio.wav')
    checks['interpreted_pcm'] = pcm(out/'interpreted144/audio.wav') == pcm(out/'direct144/audio.wav')
    paths = [Path(__file__), reference, base/'build-report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  final_field=fatal, observations=observations, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
