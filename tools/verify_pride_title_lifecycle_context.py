"""Verify title handoff and old private saves use ordinary new-game loading."""
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
    base = ROOT/'build/pride-title-lifecycle'
    out = base/'context'
    out.mkdir()
    bound(base/'build-report.json')
    reference = ROOT/'build/pride-title-start-context/report.json'
    row = bound(reference)
    prototype = row['commands'][1]
    control = reference.parent/'cleared'
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    commands = []
    checks = {}
    observations = {}
    for name in ('normal', 'interpreted'):
        folder = out/name
        folder.mkdir()
        cmd = prototype.copy()
        cmd[0] = str(base/'player.exe')
        if name == 'interpreted':
            cmd += ['--lle']
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=dict(active, TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv')),
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        events = list(csv.DictReader((folder/'exit.csv').open()))
        observations[name] = dict(fast_events=sum(r['kind'] == 'fast' for r in events),
                                  scene=json.loads((folder/'scene.json').read_text())['latched_gameplay'])
        checks[name+'/no_continue_reload'] = observations[name]['fast_events'] == 0
        checks[name+'/clean_guest'] = len(hashes(folder/'run.log')) == 2 and hashes(folder/'run.log') == hashes(control/'run.log')
        checks[name+'/clean_client'] = pixels(folder/'window.png') == pixels(control/'window.png')
        checks[name+'/clean_pcm'] = pcm(folder/'audio.wav') == pcm(control/'audio.wav')
        commands.append(cmd)
    folder = out/'fresh-title'
    folder.mkdir()
    cmd = row['commands'][0].copy()
    cmd[0] = str(base/'player.exe')
    cmd[cmd.index('--save-at')+2] = str(folder/'title.state')
    for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
        cmd[cmd.index(flag)+1] = str(folder/filename)
    with (folder/'run.log').open('wb') as log:
        subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    commands.append(cmd)
    raw = (folder/'title.state').read_bytes()
    size = struct.unpack_from('<I', raw, 20)[0]
    metadata = struct.unpack_from('<IIIII', raw, 96+size+96)
    checks['title_no_episode'] = metadata[1:] == (0, 0, 0, 0)
    checks['title_guest_unchanged'] = hashes(folder/'run.log') == hashes(reference.parent/'save/run.log')
    checks['title_client_unchanged'] = pixels(folder/'window.png') == pixels(reference.parent/'save/window.png')
    checks['title_pcm_unchanged'] = pcm(folder/'audio.wav') == pcm(reference.parent/'save/audio.wav')
    paths = [Path(__file__), base/'build-report.json', reference]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  observations=observations, commands=commands, public_player_changed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, observations, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
