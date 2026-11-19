"""Continue a complete installed-session checkpoint with compact reusable evidence.

Only accepts whole-session, per-poll fixtures. Custom frame controls and backend
extraction deliberately remain separate from unchanged original-route evidence.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import time
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import USER32, hashes, window_for
from windows_capture import capture_client
from windows_json_pipe import JsonPipe


def observe(args):
    seed = args.seed.resolve()
    out = args.out.resolve()
    state, tape = seed / 'after.state', seed / 'remaining.tape'
    with state.open('rb') as stream:
        assert stream.read(8) == b'TLKFSV01', 'Use the complete installed-session wrapper.'
    assert tape.is_file(), 'Seed needs its exact remaining per-poll tape.'
    cmd = json.loads((seed / 'command.json').read_text())
    assert '--input-polled' in cmd, 'Custom per-frame fixtures are separate.'
    start = int(re.findall(r'saved_state=.* at_frame=(\d+)', (seed / 'run.log').read_text())[-1])
    assert args.end > start
    if args.exe:
        cmd[0] = str(args.exe.resolve())
    out.mkdir()

    def replace(flag, *values):
        if flag in cmd:
            index = cmd.index(flag)
            cmd[index + 1:index + 1 + len(values)] = [str(v) for v in values]
        else:
            cmd.extend([flag, *map(str, values)])

    replace('--load', state)
    replace('--input-polled', tape)
    replace('--frames', args.end)
    replace('--hash-at', args.end)
    replace('--dump-window', out / 'window.png')
    replace('--dump-scene', out / 'scene.json')
    replace('--dump-png', out / 'native.png')
    if args.no_save:
        if '--save-at' in cmd:
            index = cmd.index('--save-at')
            del cmd[index:index + 3]
    else:
        replace('--save-at', args.end, out / 'after.state')
    # Produce a bounded PCM segment for stem observation, not a long recording.
    replace('--wav', out / 'mix.wav')
    replace('--wav-seconds', min(90, (args.end - start + 59) // 60 + 3))
    for flag in ['--no-pace', '--no-audio']:
        if flag in cmd:
            cmd.remove(flag)
    if not args.real_window:
        cmd.extend(['--no-pace', '--no-audio'])
    (out / 'command.json').write_text(json.dumps(cmd, indent=2))

    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['SDL_AUDIODRIVER'] = 'dummy'
    if not args.real_window:
        env['SDL_VIDEODRIVER'] = 'dummy'
    for key, filename in {
        'TLK_BG_TRACE': 'background.csv', 'TLK_MUSIC_START_TRACE': 'starts.csv',
        'TLK_AUDIO_STEMS': 'stems.csv', 'TLK_AUDIO_EVENTS': 'events.csv',
        'TLK_MD_SOUND_COMMANDS': 'commands.csv', 'TLK_BONUS_RESULT_TRACE': 'result.csv',
        'TLK_SPRITE_REPORT': 'sprites.json', 'TLK_FALLBACK_LOG': 'fallbacks.jsonl',
    }.items():
        env[key] = str(out / filename)

    targets = []
    for value in args.capture:
        name, field, descriptor = value.split(':')
        assert args.real_window and name.replace('-', '').isalnum()
        targets.append((name, int(field), int(descriptor, 16)))
    pipe = JsonPipe(out / 'progress.jsonl.gz') if targets else None
    if pipe:
        USER32.SetProcessDPIAware()
        env['TLK_SOFT_TREE_LOG'] = pipe.name
    taken, timed_out = {}, False
    try:
        with (out / 'run.log').open('wb') as log:
            proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                began = time.monotonic()
                while proc.poll() is None:
                    if time.monotonic() - began > args.max_seconds:
                        timed_out = True
                        proc.terminate()
                        break
                    if pipe:
                        row, hwnd = pipe.latest(), window_for(proc.pid)
                        if row and hwnd:
                            for name, field, descriptor in targets:
                                if name in taken or row['field'] < field or row['descriptor'] != descriptor:
                                    continue
                                try:
                                    first = row['field']
                                    capture_client(hwnd, out / (name + '-actual.png'))
                                    taken[name] = dict(fields=[first, pipe.latest()['field']],
                                                       descriptor=descriptor)
                                    print('capture', name, taken[name], flush=True)
                                except AssertionError:
                                    if proc.poll() is not None:
                                        break
                    time.sleep(.005 if pipe else .05)
                proc.wait(timeout=5)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
    finally:
        if pipe:
            pipe.finish()

    def read(filename):
        path = out / filename
        return list(csv.DictReader(path.open())) if path.exists() else []

    transitions, last = [], None
    for row in read('background.csv'):
        key = tuple(row[k] for k in ['stage', 'level', 'descriptor'])
        if key != last:
            transitions.append(row)
            last = key
    sources = [Path(__file__), state, tape, seed / 'command.json', Path(cmd[0]),
               Path(cmd[cmd.index('--resource-profile') + 1])]
    report = dict(result='OBSERVED_INSTALLED_NEARBY_CONTINUATION', exit_code=proc.returncode,
                  timed_out=timed_out, start=start, end=args.end, captures=taken,
                  transitions=transitions, music_starts=read('starts.csv'),
                  scope='Complete same-source installed session and exact remaining per-poll input. '
                        'No backend/schema extraction or guest edits. Captures require the incoming descriptor; '
                        'names alone do not prove active initialization or artwork. Audio stems can include FX; '
                        'owned bonus mixer gaps do not prove silence. Observation requires review, not a final TAS pass.',
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in sources})
    if proc.returncode == 0:
        report['hashes'] = hashes(out / 'run.log')
        report['ending'] = json.loads((out / 'scene.json').read_text())['latched_gameplay']
        if not args.no_save:
            used = int(re.findall(r'tape_words_used=(\d+)', (out / 'run.log').read_text())[-1])
            (out / 'remaining.tape').write_bytes(tape.read_bytes()[used * 2:])
            report['consumed'] = used
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'source_sha256'}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--max-seconds', type=int, default=300)
    parser.add_argument('--real-window', action='store_true')
    parser.add_argument('--no-save', action='store_true')
    parser.add_argument('--capture', action='append', default=[], metavar='NAME:FIELD:HEX_DESCRIPTOR')
    observe(parser.parse_args())
