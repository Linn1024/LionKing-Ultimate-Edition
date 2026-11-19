"""Compare the selectable cub roar with unmodified original MD captures.

Requires pride_movement_audit.py --source md --settle-frames 256 --tail-frames 64
output in build/pride-animation, plus the local sprite catalog. No guest edits.
"""
import csv
import hashlib
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out = ROOT/'build/pride-roar-behavior'
    out.mkdir(parents=True, exist_ok=True)
    original_path = ROOT/'build/pride-animation/md.json'
    capture = json.loads(original_path.read_text())
    assert capture['settle_frames'] == 256 and capture['tail_frames'] == 64
    original = capture['cases']['roar']
    assert len(original) == 128 and all('roar_active' in row for row in original)
    catalog = json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    pairs = {int(row['snes'], 16): {int(pose, 16) for pose in row['md']}
             for group in ('exact_matches', 'pixel_art_variants') for row in catalog[group]}
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    tape = out/'input.tape'
    pads = [0]*2456 + [0]*16 + [0x80]*20 + [0]*92
    tape.write_bytes(struct.pack('<' + str(len(pads)) + 'H', *pads))
    runs = {}
    save_checks = []
    for sound in ('snes', 'md'):
        profile = out/(sound+'.ini')
        profile.write_text('schema = 1\ngame = snes\ngameplay.simba.roar = md\n'
                           + ('audio.effects.simba.roar = md\n' if sound == 'md' else ''))
        base = ['--rom', str(ROOT/'Lion King, The (USA).sfc'), '--md-rom',
                str(ROOT/'Lion King, The (World).md'), '--resource-profile', str(profile)]
        state = out/(sound+'-ready.state')
        with (out/(sound+'-prepare.log')).open('wb') as log:
            subprocess.run([str(ROOT/'dist/LionKing.exe'), *base, '--config', str(config),
                            '--practice-level', '0', '--frames', '2200', '--save-at', '2200',
                            str(state), '--no-pace', '--no-audio', '--no-record'], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        assert struct.unpack_from('<I', state.read_bytes(), 32)[0] & 16
        for mode in ('aot', 'lle'):
            folder = out/(sound+'-'+mode)
            folder.mkdir(exist_ok=True)
            env = os.environ.copy()
            env.update(TLK_WRAM_DUMP=','.join(map(str, range(2457, 2585))),
                       TLK_WRAM_DIR=str(folder), TLK_ROAR_TRACE=str(folder/'roar.csv'))
            logpath = folder/'game.log'
            with logpath.open('wb') as log:
                subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'), *base,
                                '--load', str(state), '--frames', '2584', '--input', str(tape),
                                *(['--lle'] if mode == 'lle' else [])], cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
            gameplay = []
            for index, expected in enumerate(original):
                ram = (folder/f'hl_wram_{2457+index}.bin').read_bytes()
                word = lambda a: struct.unpack_from('<H', ram, a)[0]
                draw = word(0xb21f)
                pose = int.from_bytes(ram[draw+10:draw+13], 'little') & 0x3fffff
                if index >= 17:
                    assert expected['pose'] in pairs.get(pose, set()), (sound, mode, index, hex(pose))
                assert word(0xa698) == expected['roar_active'], (sound, mode, index, 'active window')
                gameplay.append([pose, word(0xa698), word(0xb21b), word(0xb21d), word(0x1ffa2)])
            trace = list(csv.DictReader((folder/'roar.csv').open()))
            assert {row['value'] for row in trace if row['event'] == 'activation_delay'} == {'14'}
            assert sum(row['event'] == 'voice_at_activation' for row in trace) == 1
            runs[sound+'-'+mode] = {'hashes': hashes(logpath), 'gameplay': gameplay}
            print(sound, mode, '111 original poses and 128 active-window fields PASS', flush=True)
        # Preserve guest continuation immediately before/at/after activation,
        # near the end of the action, and after it returns to idle.
        # No guest fields are edited.
        for frame in (2487, 2488, 2489, 2508, 2528, 2529):
            checkpoint = out/f'{sound}-{frame}.state'
            logpath = out/f'{sound}-{frame}-save.log'
            command = [str(ROOT/'engine/build-win/tlk_headless.exe'), *base,
                       '--load', str(state), '--frames', '2584', '--input', str(tape)]
            with logpath.open('wb') as log:
                subprocess.run([*command, '--save-at', str(frame), str(checkpoint)], cwd=ROOT,
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
            assert hashes(logpath) == runs[sound+'-aot']['hashes']
            assert struct.unpack_from('<I', checkpoint.read_bytes(), 32)[0] & 16
            for mode in ('aot', 'lle'):
                resumed = out/f'{sound}-{frame}-{mode}-resumed.log'
                with resumed.open('wb') as log:
                    subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'), *base,
                                    '--load', str(checkpoint), '--frames', '2584', '--input', str(tape),
                                    *(['--lle'] if mode == 'lle' else [])], cwd=ROOT,
                                   stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
                assert hashes(resumed) == runs[sound+'-aot']['hashes'], (sound, frame, mode, 'resume')
            save_checks.append([sound, frame])
    reference = runs['snes-aot']['gameplay']
    assert all(row['gameplay'] == reference for row in runs.values()), 'Sound choice changed the action'
    for sound in ('snes', 'md'):
        assert runs[sound+'-aot']['hashes'] == runs[sound+'-lle']['hashes']
    report = {'result': 'PASS', 'scope': __doc__, 'original_pose_fields': 111,
              'original_md_capture_sha256': hashlib.sha256(original_path.read_bytes()).hexdigest(),
              'original_active_window_fields': 128, 'independent_sound_choices': True,
              'animation_parser': 'Original compiled body; five post-load resource hooks',
              'mid_action_source_matched_saves': save_checks,
              'runs': {key: row['hashes'] for key, row in runs.items()}}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
