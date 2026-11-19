"""Verify the independently built final-scene player through actual Windows clients."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import wave
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes, pixels


def pcm(path):
    with wave.open(str(path), 'rb') as stream:
        return stream.readframes(stream.getnframes())


def main():
    base = ROOT/'build/pride-final-standalone'
    out = base/'verification'
    out.mkdir()
    build = base/'build-report.json'
    bound(build)
    reference = ROOT/'build/pride-final-scene-compiled-probe/fresh-compiled'
    prior = bound(reference/'report.json')
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    enabled = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1',
                   TLK_FINAL_FAST_ASSETS='1', TLK_FINAL_SCENE_PRESENT='1',
                   TLK_CONTINUE_FAST_RELOAD='1', TLK_CONTINUE_BANK_APPLY='1',
                   TLK_CONTINUE_TRANSITION='1')
    commands = []
    checks = {}
    saved = out/'continue.state'
    for name, end, restore, traced in [('plain', 4494, False, False),
                                      ('traced', 4494, False, True),
                                      ('save420', 4314, False, False),
                                      ('resume', 4494, True, False)]:
        folder = out/name
        folder.mkdir()
        cmd = prior['command'].copy()
        cmd[0] = str(base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(end)
        for flag, filename in [('--dump-window', 'window.png'),
                               ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        if restore:
            cmd += ['--load', str(saved)]
        elif name == 'save420':
            cmd += ['--save-at', str(end), str(saved)]
        env = dict(enabled)
        if traced:
            env.update(TLK_CONTINUE_BANK_DIR=str(folder),
                       TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
                       TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=180,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
        if name != 'traced':
            checks[name+'/no_research_sidecars'] = not any(
                folder.glob('*.csv')) and not any(folder.glob('*.bin')) and not any(folder.glob('*.record'))
        print(name, 'completed', flush=True)
    for name in ('plain', 'traced', 'resume'):
        folder = out/name
        checks[name+'/guest_endpoint'] = hashes(folder/'run.log') == hashes(reference/'run.log')
        checks[name+'/actual_client'] = pixels(folder/'window.png') == pixels(reference/'window.png')
        scene = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        checks[name+'/playable_pride'] = (scene['descriptor'] == 903 and scene['player'] == [64, 1255]
                                         and scene['health'] == 4 and scene['lives'] == 2)
    for name in ('plain', 'traced'):
        checks[name+'/full_pcm'] = pcm(out/name/'audio.wav') == pcm(reference/'audio.wav')
    rows = list(csv.DictReader((out/'traced/transition.csv').open()))
    old_rows = list(csv.DictReader((reference/'transition.csv').open()))
    checks['unchanged_transition_timeline'] = len(rows) == 477 and rows == old_rows
    checks['single_file_save'] = saved.read_bytes()[:8] == b'TLKFSV01'
    checks['cold_resume_pcm'] = pcm(out/'save420/audio.wav') + pcm(out/'resume/audio.wav') == pcm(reference/'audio.wav')
    fade = ROOT/'build/pride-final-scene-compiled-probe/capture/420/window.png'
    checks['save_during_visible_fade'] = pixels(out/'save420/window.png') == pixels(fade)
    paths = [Path(__file__), build, reference/'report.json',
             ROOT/'build/pride-final-scene-compiled-probe/capture/report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  commands=commands, public_player_changed=False,
                  resources_activated=False, native256_ordinary_pride_only=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
