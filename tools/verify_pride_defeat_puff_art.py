"""Verify independently selected shared defeat-puff art on ordinary Pride inputs.

The alternate-bank state is explicitly a controlled guard fixture, not ordinary
gameplay or completion evidence. All other actions use the existing input tape.
"""
import csv
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data
from pride_defeat_puff_art import PAIRS

LEAF = 'graphics.sprites.effects.defeat_puff'


def main():
    out = ROOT/'build/pride-defeat-puff-art'
    out.mkdir(parents=True, exist_ok=True)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    profiles = {}
    choices = {'native': '', 'frames': LEAF+'.frames = md\n', 'palette': LEAF+'.palette = md\n',
               'both': LEAF+' = md\n', 'other-enemies': 'graphics.sprites.enemies.other = md\n',
               'simba-palette': 'graphics.sprites.simba.cub.palette = md\n'}
    for name, choice in choices.items():
        profiles[name] = out/(name+'.ini')
        profiles[name].write_text('schema = 1\ngame = snes\n'+choice)
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    ready = out/'ready.state'
    base = ['--rom', ROOT/'Lion King, The (USA).sfc', '--md-rom', ROOT/'Lion King, The (World).md']
    head = ROOT/'engine/build-win/tlk_headless.exe'
    with (out/'prepare.log').open('wb') as log:
        subprocess.run(list(map(str, [head, *base, '--resource-profile', profiles['native'], '--frames', 1400,
                                     '--input-polled', tape, '--save-at', 1400, ready])),
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    consumed = int(re.search(r'tape_words_used=(\d+)', (out/'prepare.log').read_text()).group(1))
    suffix = out/'after1400.polled.tape'
    suffix.write_bytes(tape.read_bytes()[consumed*2:])

    def run(name, source, end, state=ready, inputs=suffix, extra=()):
        env = os.environ.copy()
        env.update(TLK_SPRITE_REPORT=str(out/(name+'-coverage.json')),
                   TLK_SPRITE_OBJECTS=str(out/(name+'-objects.csv')))
        command = [ROOT/'dist/LionKing.exe', *base, '--resource-profile', profiles[source], '--config', config,
                   '--no-pace', '--no-audio', '--no-record', '--load', state, '--input-polled', inputs,
                   '--frames', end, '--dump-window', out/(name+'.png'), '--dump-scene', out/(name+'.json'),
                   '--wav', out/(name+'.wav'), *extra]
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run(list(map(str, command)), cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=120)
        return {'hashes': hashes(out/(name+'.log')),
                'coverage': json.loads((out/(name+'-coverage.json')).read_text()),
                'scene': json.loads((out/(name+'.json')).read_text()),
                'pixels': pixels(out/(name+'.png')), 'wav': wav_data(out/(name+'.wav'))}

    def rectangle(piece):
        x, y = piece['screen']
        size = piece['size']
        return x*2, y*2, (x+size)*2, (y+size)*2

    def inside(index, width, boxes):
        x, y = index%width, index//width
        return any(a <= x < c and b <= y < d for a, b, c, d in boxes)

    palette_words = struct.unpack_from('<16H', (ROOT/'Lion King, The (USA).sfc').read_bytes(), 0x7b93)
    expected_colors = ''.join(f'{c:04x}' for c in palette_words[1:])
    phases = []
    for phase, (pose, _) in enumerate(PAIRS):
        end = 1431+phase*4
        results = {source: run(f'{phase}-{source}', source, end) for source in choices}
        native = results['native']
        assert native['scene']['level'] == 0 and native['scene']['stage_detected']
        assert len(native['hashes']) == 2
        assert all(r['hashes'] == native['hashes'] and r['wav'] == native['wav'] for r in results.values()), 'Art changed guest/audio'
        pieces = [p for p in native['scene']['pieces'] if p['pose'] == pose and not p['fixed']]
        assert pieces and all(p['palette'] == 0 for p in pieces), ('Wrong painted phase', phase, end)
        boxes = [rectangle(p) for p in pieces]
        w, h, original = native['pixels']
        assert (w, h) == (512, 448)
        changes = {}
        for source in ('frames', 'palette', 'both'):
            row = results[source]
            assert row['pixels'][:2] == (w, h)
            changed = [i for i, (a, b) in enumerate(zip(original, row['pixels'][2])) if a != b]
            assert all(inside(i, w, boxes) for i in changed), (phase, source, 'Change escaped puff pieces')
            changes[source] = len(changed)
            assert row['coverage']['seen_by_role']['defeat_puff'] == (phase+1 if source in ('frames', 'both') else 0)
        # Sibling choices can change their actors even when they overlap the
        # effect's bounds. Compare only effect area outside all other pieces.
        other_boxes = [rectangle(p) for p in native['scene']['pieces'] if p['object'] != pieces[0]['object']]
        visible_region = [i for i in range(w*h) if inside(i, w, boxes) and not inside(i, w, other_boxes)]
        assert visible_region
        for sibling in ('other-enemies', 'simba-palette'):
            assert results[sibling]['coverage']['seen_by_role']['defeat_puff'] == 0
            assert all(original[i] == results[sibling]['pixels'][2][i] for i in visible_region), (phase, sibling, 'Sibling recoloured the puff')
        observations = list(csv.DictReader((out/f'{phase}-native-objects.csv').open()))
        matching = [r for r in observations if int(r['pose'], 16) == pose]
        assert matching and all(r['palette'] == '0' and r['colors'][4:] == expected_colors for r in matching)
        lle = run(f'{phase}-lle', 'both', end, extra=['--lle'])
        assert lle == results['both'], (phase, 'Compiled/interpreted rendering differs')
        phases.append({'native_pose': pose, 'rendered_frame': end, 'changed_pixels': changes,
                       'sibling_isolation_pixels_checked': len(visible_region), 'native_live_palette_checked': True})
        print('Defeat-puff phase', phase+1, 'independent windows, live palette, unchanged guest/WAV and AOT/LLE PASS', flush=True)
    assert sum(p['changed_pixels']['palette'] for p in phases) > 100, 'MD palette choice was invisible'

    saves = []
    for frame in (1433, 1459):
        continuous = run(f'{frame}-continuous', 'both', frame+1)
        for source in ('native', 'both'):
            state = out/f'{frame}-{source}.state'
            name = f'{frame}-{source}-save'
            saved = run(name, source, frame, extra=['--save-at', frame, state])
            used = int(re.search(r'tape_words_used=(\d+)', (out/(name+'.log')).read_text()).group(1))
            after = out/f'{frame}-{source}-after.polled.tape'
            after.write_bytes(suffix.read_bytes()[used*2:])
            loaded = run(f'{frame}-{source}-loaded', 'both', frame+1, state, after)
            assert loaded['hashes'] == continuous['hashes'] and loaded['scene'] == continuous['scene'] and loaded['pixels'] == continuous['pixels']
            assert loaded['wav'] == continuous['wav'][len(saved['wav']):], 'First loaded native audio field differs'
            saves.append({'frame': frame, 'source': source})

    # Explicitly controlled guard: repurpose only the original draw's palette
    # bits after initialization. Preserve the guest action and all source IDs.
    state = out/'bank-prepare.state'
    env = os.environ.copy()
    env.update(TLK_WRAM_DUMP='1430', TLK_WRAM_DIR=str(out))
    command = [head, *base, '--resource-profile', profiles['native'], '--load', ready, '--frames', 1430,
               '--input-polled', suffix, '--save-at', 1430, state]
    with (out/'bank-prepare.log').open('wb') as log:
        subprocess.run(list(map(str, command)), cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    used = int(re.search(r'tape_words_used=(\d+)', (out/'bank-prepare.log').read_text()).group(1))
    after = out/'bank-after.polled.tape'
    after.write_bytes(suffix.read_bytes()[used*2:])
    ram = (out/'hl_wram_1430.bin').read_bytes()
    actor = json.loads((ROOT/'build/lizard-defeat-original/native.json').read_text())['entries'][0]['actor']
    draw = struct.unpack_from('<H', ram, actor+12)[0]
    raw = bytearray(state.read_bytes())
    at = raw.find(ram)
    assert at >= 0 and raw.find(ram, at+1) < 0
    old = struct.unpack_from('<H', raw, at+draw+8)[0]
    # Object flags use bits1..3; the original draw path shifts the low byte
    # into the final OAM attribute high byte. Do not change high-byte flags.
    struct.pack_into('<H', raw, at+draw+8, old & ~0xe | 2)
    patched = out/'controlled-bank1.state'
    patched.write_bytes(raw)
    # Let the original native renderer latch the new bank before saving. The
    # earlier snapshot still legitimately contains bank0 presentation history.
    warmed = out/'controlled-bank1-latched.state'
    with (out/'bank-warm.log').open('wb') as log:
        subprocess.run(list(map(str, [head, *base, '--resource-profile', profiles['native'], '--load', patched,
                                     '--frames', 1432, '--input-polled', after, '--save-at', 1432, warmed])),
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    used = int(re.search(r'tape_words_used=(\d+)', (out/'bank-warm.log').read_text()).group(1))
    warm_after = out/'bank-latched-after.polled.tape'
    warm_after.write_bytes(after.read_bytes()[used*2:])
    native = run('bank-native', 'native', 1433, warmed, warm_after)
    external = run('bank-selected', 'both', 1433, warmed, warm_after)
    assert any(p['pose'] == PAIRS[0][0] and p['palette'] == 1 for p in native['scene']['pieces']), 'Alternate-bank fixture did not produce that native draw'
    assert native['hashes'] == external['hashes'] and native['pixels'] == external['pixels'] and native['wav'] == external['wav']
    assert external['coverage']['seen_by_role']['defeat_puff'] == 0
    assert any(p['pose'] == PAIRS[0][0] and p['palette'] == 1 for p in external['scene']['pieces'])
    report = {'result': 'PASS', 'scope': __doc__, 'source_id': LEAF, 'original_phases': phases,
              'source_choices_independent': True, 'all_guest_and_native_wav_bytes_unchanged': True,
              'compiled_interpreted_windows_identical': True, 'first_loaded_fields': saves,
              'controlled_unreviewed_palette_bank_retains_native_window': True}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Four puff save continuations and controlled palette-bank fallback PASS', flush=True)


if __name__ == '__main__':
    main()
