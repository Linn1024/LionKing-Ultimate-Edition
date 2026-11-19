"""Inactive Pride camera/contact choices must not change later-level gameplay.

Uses the unmodified controller fixture prepared by verify_graveyard_scenery.py.
The explicit widescreen spawn option remains an independent gameplay change.
"""
import json
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out = ROOT / 'build/camera-scene-scope'
    out.mkdir(parents=True, exist_ok=True)
    fixture = ROOT / 'build/graveyard-verification'
    state = fixture / 'moving.state'
    tape = fixture / 'after13500.polled.tape'
    assert state.exists() and tape.exists(), 'Run verify_graveyard_scenery.py first'
    config = out / 'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    results = {}
    for source, choice in [('snes', 'gameplay.camera = snes\n'),
                           ('md', 'gameplay.camera = md\n'),
                           ('contacts', 'gameplay.levels.pride_lands.contacts = md\n')]:
        profile = out / (source + '.ini')
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n' + choice)
        modes = ['headless-aot', 'headless-lle', 'sdl']
        if source == 'snes':
            modes.append('headless-wide-spawn')
        for mode in modes:
            name = source + '-' + mode
            host = ROOT / ('dist/LionKing.exe' if mode == 'sdl' else 'engine/build-win/tlk_headless.exe')
            log = out / (name + '.log')
            cmd = [str(host), '--rom', str(ROOT / 'Lion King, The (USA).sfc'),
                   '--md-rom', str(ROOT / 'Lion King, The (World).md'),
                   '--resource-profile', str(profile), '--load', str(state),
                   '--input-polled', str(tape), '--frames', '14400']
            if mode == 'sdl':
                cmd += ['--config', str(config), '--no-pace', '--no-audio', '--no-record',
                        '--dump-scene', str(out / (name + '.json'))]
            if mode == 'headless-lle':
                cmd.append('--lle')
            if mode == 'headless-wide-spawn':
                cmd.append('--wide-spawn')
            with log.open('wb') as stream:
                subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                               check=True, timeout=180)
            results[name] = hashes(log)
            assert len(results[name]) == 2, name + ' has no final hashes'
            if mode == 'sdl':
                scene = json.loads((out / (name + '.json')).read_text())
                assert scene['level'] == 2 and scene['stage_detected'], 'Wrong scene fixture'
    assert all(v == results['snes-headless-aot'] for k, v in results.items()
               if k != 'snes-headless-wide-spawn'), results
    assert results['snes-headless-wide-spawn'] != results['snes-headless-aot'], \
        'Explicit widescreen spawning no longer changes the verified fixture'
    (out / 'report.json').write_text(json.dumps({'result': 'PASS', 'scene': 2,
                                               'host_source_hashes': results}, indent=2) + '\n')
    print('Inactive Pride camera/contact sources preserve later-level gameplay across both hosts and modes PASS', flush=True)


if __name__ == '__main__':
    main()
