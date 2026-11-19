"""Focused current-launcher review of the three death/Timon reports."""
import json
import os
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import USER32, hashes, window_for
from windows_capture import capture_client
from windows_json_pipe import JsonPipe

out = ROOT / 'build/fidelity5629-current-death-timon'
out.mkdir(exist_ok=True)
USER32.SetProcessDPIAware()
env = {k: v for k, v in os.environ.items()
       if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
env['SDL_AUDIODRIVER'] = 'dummy'
player = ROOT / 'dist/installed-preview5627/LionKing.exe'
runs = {}
for name, points in [('timon', [1020]), ('respawn', [2778]),
                     ('cub', [2300, 2340]), ('adult', [3790, 3860]),
                     ('nested', [30170, 30240])]:
    p = out / name
    p.mkdir(exist_ok=True)
    seed = ROOT / 'build/current-death-timon-review2' / name
    if name == 'timon':
        seed = ROOT / 'build/fidelity5619-timon-art-controls/md'
    cmd = json.loads((seed / 'command.json').read_text())
    cmd[0] = str(player)
    values = {'--dump-window': p / 'window.png',
              '--dump-scene': p / 'scene.json', '--dump-png': p / 'native.png',
              '--sprite-assets': ROOT / 'build/fidelity5617-timon-helper/sprites.assets'}
    if name == 'timon':
        values.update({'--load': seed / 'after.state', '--frames': 1050,
                       '--hash-at': 1050, '--save-at': 1050})
    for flag, value in values.items():
        cmd[cmd.index(flag) + 1] = str(value)
    cmd[cmd.index('--save-at') + 2] = str(p / 'after.state')
    if '--wav' in cmd:
        cmd[cmd.index('--wav') + 1] = str(p / 'mix.wav')
    (p / 'headless-command.json').write_text(json.dumps(cmd, indent=2))
    if not (p / 'headless.log').exists():
        with (p / 'headless.log').open('wb') as f:
            subprocess.run(cmd, cwd=ROOT, env=dict(env, SDL_VIDEODRIVER='dummy'),
                           stdout=f, stderr=subprocess.STDOUT, check=True, timeout=55)
    expected = dict(guest=hashes(p / 'headless.log'),
                    picture=digest(p / 'window.png'))
    historical = None if name == 'timon' else dict(
        guest=hashes(p / 'headless.log') == hashes(seed / 'headless.log'),
        picture=digest(p / 'window.png') == digest(seed / 'window.png'),
        native_ppu=digest(p / 'native.png') == digest(seed / 'native.png'))
    for flag in ['--no-audio', '--no-pace']:
        if flag in cmd:
            cmd.remove(flag)
    (p / 'window-command.json').write_text(json.dumps(cmd, indent=2))
    if (p / 'progress.jsonl.gz').exists():
        runs[name] = dict(captures=[[1020, 1028]],
                         own_guest=hashes(p / 'window.log') == expected['guest'],
                         own_picture=digest(p / 'window.png') == expected['picture'],
                         historical=historical)
        continue
    pipe = JsonPipe(p / 'progress.jsonl.gz')
    taken = []
    try:
        with (p / 'window.log').open('wb') as f:
            proc = subprocess.Popen(cmd, cwd=ROOT, env=dict(env, TLK_SOFT_TREE_LOG=pipe.name),
                                    stdout=f, stderr=subprocess.STDOUT,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            start = time.monotonic()
            try:
                while proc.poll() is None:
                    assert time.monotonic() - start < 55
                    row, hwnd = pipe.latest(), window_for(proc.pid)
                    if row and hwnd and len(taken) < len(points) and row['field'] >= points[len(taken)]:
                        first = row['field']
                        capture_client(hwnd, p / ('actual-' + str(len(taken)) + '.png'))
                        taken.append([first, pipe.latest()['field']])
                    time.sleep(.004)
                assert proc.returncode == 0
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=3)
    finally:
        pipe.finish()
    runs[name] = dict(captures=taken, own_guest=hashes(p / 'window.log') == expected['guest'],
                      own_picture=digest(p / 'window.png') == expected['picture'],
                      historical=historical)
    print(name, runs[name], flush=True)
checks = dict(actual_windows=all(len(r['captures']) in [1, 2] and r['own_guest'] and r['own_picture']
                                 for r in runs.values()),
              previous_death_respawn_preserved=all(all(r['historical'].values())
                                                   for r in runs.values() if r['historical']))
(out / 'report.json').write_text(json.dumps(dict(
    result='PASS_CURRENT_DEATH_TIMON' if all(checks.values()) else 'INCOMPLETE',
    binary_sha256=digest(player), checks=checks, runs=runs,
    scope='Current published launcher; intact native4 death fixtures and current full Timon save. '
          'Actual paced Windows with ordinary dummy audio callback and own headless endpoints. '
          'Historical death/respawn guest/nativePPU/presentation comparisons; no audio equality '
          'claim across later sound fixes. Shared main-level source routing previously checked; '
          'not ten independent natural-death walkthroughs. Images require visual review.'), indent=2))
assert all(checks.values())
