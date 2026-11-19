"""Verify independent Pride game-over music on ordinary Windows playthroughs.

Hard difficulty loses the final life and shows GAME OVER. Normal difficulty
loses three lives, shows CONTINUE, accepts YES and restarts through the original
loader. Complete runs never load states or edit gameplay. Separate saved phases
verify exact audio/guest continuation, including the original continue input.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import audio_offset, wav_data


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def make_inputs(out):
    # Original ordinary Options/new-game macros, without debug-level selection.
    sys.path.insert(0, str(ROOT/'engine/tools'))
    import make_play_tapes as macros
    # Own a bounded original-prefix capture. The full regression runner writes
    # its All Bugs RAM concurrently and must not be used as a mutable fixture.
    source = out/'credited-prefix.ram'
    native_profile = out/'source-native.ini';native_profile.write_text('schema = 1\ngame = snes\n')
    command = [ROOT/'engine/build-win/tlk_headless.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
               '--resource-profile', native_profile, '--lle', '--input-polled', ROOT/'engine/tapes/allbugsF.read.tape',
               '--frames', '3740', '--ram-log', source]
    with (out/'credited-prefix.log').open('wb') as log:
        subprocess.run(list(map(str, command)), cwd=ROOT, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=180)
    rows = [r.split() for r in source.read_text().splitlines()]
    hard = macros.t_difficulty(1, play=0)+[int(r[8], 16) for r in rows if 930 <= int(r[0]) <= 3740]+[0]*2500
    normal = (macros.t_difficulty(0, play=0)+([0x100]*240+[0x200]*240)*12)[:4000]
    normal += [0]*500+[0x200]*2+[0]*10+[0x80]*2+[0]*900
    paths = {}
    for name, words in [('hard', hard), ('normal', normal)]:
        path = out/(name+'.tape')
        path.write_bytes(struct.pack('<'+'H'*len(words), *words))
        paths[name] = path
    (out/'input-provenance.json').write_text(json.dumps({
        'scope': 'Ordinary Options difficulty/new game plus controller inputs only; no debug or loaded states',
        'hard_gameplay_pad_source': 'Existing credited ShgofcTAS All Bugs recording, frames930..3740, then neutral',
        'normal_gameplay': 'Walk right/left, neutral on continue screen, select YES with Left and A',
        'source_ram_sha256': digest(source), 'source_headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
        'source_tape_sha256': digest(ROOT/'engine/tapes/allbugsF.read.tape'),
        'macro_source_sha256': digest(ROOT/'engine/tools/make_play_tapes.py'),
        'tapes_sha256': {name: digest(path) for name, path in paths.items()}}, indent=2)+'\n')
    return paths


def main():
    out = ROOT/'build/pride-game-over-music';out.mkdir(exist_ok=True)
    report_path = out/'report.json';report_path.write_text(json.dumps({'result': 'RUNNING'})+'\n')
    original_path = ROOT/'build/pride-game-over-original/report.json'
    original = json.loads(original_path.read_text())
    assert original['result'] == 'PASS' and original['no_430_on_final_life']
    assert len(original['life_losses']) == 9 and int(original['game_over_music'][0]['value']) == 327
    tapes = make_inputs(out)
    config = out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    choices = {'native': '', 'over': 'audio.music.pride_game_over = md\n',
               'leveldeath': 'audio.music.pride_lands = md\naudio.music.pride_health_death = md\n',
               'all': 'audio.music.pride_lands = md\naudio.music.pride_health_death = md\naudio.music.pride_game_over = md\n',
               'sibling': 'audio.music.be_prepared = md\n'}
    profiles = {}
    for name, extra in choices.items():
        path = out/(name+'.ini');path.write_text('schema = 1\ngame = snes\n'+extra);profiles[name] = path

    def run(name, route, profile, mode='aot', save=None, load=None):
        folder = out/name;folder.mkdir(exist_ok=True)
        env = os.environ.copy();env.update(TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),
            TLK_AUDIO_EVENTS=str(folder/'events.csv'), TLK_AUDIO_STEMS=str(folder/'stems.csv'))
        end = 3000 if route == 'hard' else 5300
        cmd = [ROOT/'dist/LionKing.exe', '--rom', ROOT/'Lion King, The (USA).sfc',
               '--md-rom', ROOT/'Lion King, The (World).md', '--resource-profile', profiles[profile],
               '--config', config, '--input', tapes[route], '--frames', str(end),
               '--no-pace', '--no-audio', '--no-record', '--wav', folder/'route.wav', '--wav-seconds', '100',
               '--dump-window', folder/'window.png', '--dump-scene', folder/'scene.json']
        if mode == 'lle': cmd.append('--lle')
        if save: cmd += ['--save-at', str(save[0]), save[1]]
        if load: cmd += ['--load', load]
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=180)
        return folder

    runs = {};full = {};saved = []
    for route in ('hard', 'normal'):
        pictures = []
        for profile in ('native', 'over', 'leveldeath', 'all'):
            modes = {}
            for mode in ('aot', 'lle'):
                state = out/f'{route}-{profile}.state'
                frame = (2750 if profile == 'over' else 2850) if route == 'hard' else 4450
                folder = run(f'{route}-{profile}-{mode}', route, profile, mode,
                             save=(frame, state) if mode == 'aot' else None)
                commands = list(csv.DictReader((folder/'driver.csv').open()))
                tracks = [int(r['value']) for r in commands if r['selector'] == '1']
                if profile == 'native': assert not commands
                assert (327 in tracks) == (profile in ('over', 'all')), (route, profile, tracks)
                if route == 'hard': assert 430 not in tracks, ('Final-life430 leak', profile, tracks)
                elif profile in ('leveldeath', 'all'): assert tracks.count(430) == 2, tracks
                if profile == 'over': assert tracks == ([327] if route == 'hard' else [327, 0]), tracks
                scene = json.loads((folder/'scene.json').read_text());guest = scene['latched_gameplay']
                assert scene['level'] == 0 and guest['age'] == 0
                if route == 'hard':
                    assert guest['descriptor'] == 0x57b and guest['health'] == guest['lives'] == 0
                else:
                    assert guest['descriptor'] == 0x387 and guest['health'] == 4 and guest['lives'] == 2, guest
                    assert guest['player'] == [64, 1255] and guest['checkpoint'][0] == 0, guest
                    if profile == 'all':
                        tail = tracks[tracks.index(327)+1:]
                        # The original level loader and player initializer
                        # each issue their native music command on continue.
                        assert tail[0] == 0 and tail[1:] and set(tail[1:]) == {137}, tracks
                if profile in ('over', 'all'):
                    stems = list(csv.DictReader((folder/'stems.csv').open()))
                    low, high = (2830, 2990) if route == 'hard' else (4370, 4490)
                    assert max(int(r['md_peak']) for r in stems if low <= int(r['frame']) <= high) > 500
                modes[mode] = {'hashes': hashes(folder/'run.log'), 'tracks': tracks,
                               'wav_sha256': digest(folder/'route.wav')}
                pictures.append(pixels(folder/'window.png'))
                if mode == 'aot':
                    full[route, profile] = folder
                    if profile in ('over', 'all'): saved.append((route, profile, frame, state))
            assert modes['aot'] == modes['lle'], (route, profile, 'AOT/LLE audio or guest differs')
            runs[f'{route}-{profile}'] = modes
            print(route, profile, 'ordinary audio/guest AOT/LLE PASS', flush=True)
        assert all(p == pictures[0] for p in pictures), route+' music changed the final picture'

    sibling = run('hard-sibling', 'hard', 'sibling')
    assert not list(csv.DictReader((sibling/'driver.csv').open())), 'Same program number aliased a different music leaf'
    # Additional playing save, distinct from the hard pre-initialization save.
    state = out/'hard-over-playing.state'
    full['hard', 'over-playing'] = run('hard-over-playing', 'hard', 'over', save=(2850, state))
    saved.append(('hard', 'over-playing', 2850, state))
    continuations = []
    for route, label, frame, state in saved:
        profile = 'over' if label == 'over-playing' else label
        raw = state.read_bytes();at = audio_offset(raw)
        track = struct.unpack_from('<I', raw, at+20)[0]
        assert struct.unpack_from('<I', raw, at+8)[0] == 2
        assert track == (0 if route == 'hard' and frame == 2750 else 327), (route, label, track)
        folder = run(f'{route}-{label}-loaded', route, profile, load=state)
        audio = wav_data(folder/'route.wav');continuous = wav_data(full[route, label]/'route.wav')
        assert audio and continuous[-len(audio):] == audio, (route, label, 'Saved WAV suffix differs')
        assert hashes(folder/'run.log') == hashes(full[route, label]/'run.log')
        continuations.append({'route': route, 'profile': profile, 'frame': frame, 'track': track, 'exact_audio_bytes': len(audio)})
        print(route, label, frame, 'new-process exact audio/guest continuation PASS', flush=True)
    changed = run('hard-changed-source', 'hard', 'native', load=out/'hard-over-playing.state')
    assert not list(csv.DictReader((changed/'driver.csv').open())), 'Foreign game-over song survived a source change'
    result = {'result': 'PASS', 'scope': __doc__, 'player_sha256': digest(ROOT/'dist/LionKing.exe'),
              'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'original_reference_sha256': digest(original_path), 'input_provenance_sha256': digest(out/'input-provenance.json'),
              'runs': runs, 'ordinary_power_on_runs': 16, 'final_life_no_430': True,
              'normal_continue_accepted_and_level_restored': True, 'saved_phases': continuations,
              'source_change_resets_md': True, 'same_program_sibling_is_independent': True,
              'all_profile_final_windows_equal': True, 'audio_schema': 2,
              'fall_death_gameplay_equivalence_claimed': False}
    report_path.write_text(json.dumps(result, indent=2)+'\n')
    print('Independent Pride continue/game-over music PASS', flush=True)


if __name__ == '__main__': main()
