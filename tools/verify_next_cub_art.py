"""Exercise independent cub art/palettes in the second and third main levels.

Uses ordinary credited All Bugs inputs, actual SDL captures and first loaded
fields. Unmapped poses remain native; this does not prove MD gameplay timing.
"""
import argparse
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adult-only', action='store_true', help='Run only the unsupported adult-scene guard check')
    parser.add_argument('--exile', action='store_true', help='Verify the independently selected Exile cub artwork')
    args = parser.parse_args()
    out = ROOT/('build/exile-cub-art' if args.exile else 'build/next-cub-art')
    out.mkdir(parents=True, exist_ok=True)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    profiles = {}
    for name, extra in {'native': '', 'frames': 'graphics.sprites.simba.cub.frames = md\n',
                        'palette': 'graphics.sprites.simba.cub.palette = md\n',
                        'both': 'graphics.sprites.simba.cub = md\n'}.items():
        profiles[name] = out/(name+'.ini')
        profiles[name].write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+extra)
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    common = ['--rom', ROOT/'Lion King, The (USA).sfc', '--md-rom', ROOT/'Lion King, The (World).md']

    def run(name, host, profile, frame, extra, capture=False):
        log = out/(name+'.log')
        cmd = [ROOT/('dist/LionKing.exe' if host == 'sdl' else 'engine/build-win/tlk_headless.exe'),
               *common, '--resource-profile', profiles[profile], '--frames', frame, *extra]
        env = os.environ.copy()
        env.update(TLK_SPRITE_REPORT=str(out/(name+'-coverage.json')),
                   TLK_WRAM_DUMP=str(frame), TLK_WRAM_DIR=str(out))
        if host == 'sdl':
            cmd += ['--config', config, '--no-pace', '--no-audio', '--no-record']
        if capture:
            cmd += ['--dump-window', out/(name+'.png'), '--dump-scene', out/(name+'.json')]
        with log.open('wb') as f:
            subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, stdout=f,
                           stderr=subprocess.STDOUT, check=True, timeout=300)
        used = re.search(r'tape_words_used=(\d+)', log.read_text())
        return hashes(log), int(used.group(1)) if used else 0

    results = {}
    # Exile's 26000 field is at the right camera clamp, where the native
    # picture sits at column64. Use a central field for the centered-palette
    # bounds assertion below, as the second/third-level fixtures do.
    routes = ((4, 25000, 25500, 25200),) if args.exile else ((1, 5000, 12000, 6000), (2, 13500, 18500, 13600))
    for level, start, end, save_frame in (() if args.adult_only else routes):
        state = out/f'{level}-start.state'
        _, used = run(f'{level}-prepare', 'head', 'native', start,
                      ['--input-polled', tape, '--save-at', start, state])
        suffix = out/f'{level}-suffix.polled.tape'
        suffix.write_bytes(tape.read_bytes()[used*2:])
        pictures = {}
        rows = {}
        for name in ('native', 'frames', 'palette', 'both', 'both-lle'):
            profile = 'both' if name == 'both-lle' else name
            key = f'{level}-{name}'
            value, _ = run(key, 'sdl', profile, end,
                           ['--load', state, '--input-polled', suffix]+(['--lle'] if name == 'both-lle' else []), True)
            scene = json.loads((out/(key+'.json')).read_text())
            assert scene['level'] == level and scene['stage_detected']
            assert any(p['position_pointer'] == 0xb21b and not p['fixed'] for p in scene['pieces'])
            coverage = json.loads((out/(key+'-coverage.json')).read_text())
            if profile in ('frames', 'both'):
                assert coverage['seen_by_role']['cub'] > 20, (key, 'MD frame path not exercised')
                assert len(coverage['seen_cub_poses']) == coverage['seen_by_role']['cub']
            else:
                assert coverage['seen_by_role']['cub'] == 0, (key, 'Unselected frame path activated')
            pictures[name] = pixels(out/(key+'.png'))
            assert pictures[name][:2] == (640, 448)
            rows[name] = {'hashes': value, 'coverage': coverage}
        assert len(rows['native']['hashes']) == 2
        assert all(r['hashes'] == rows['native']['hashes'] for r in rows.values()), 'Artwork altered the guest'
        assert pictures['both'] == pictures['both-lle'] and rows['both'] == rows['both-lle']
        # Independent palette must visibly recolour Simba, with other actors,
        # HUD and scenery untouched. These fixtures are away from view edges.
        scene = json.loads((out/f'{level}-native.json').read_text())
        cub = [p for p in scene['pieces'] if p['position_pointer'] == 0xb21b and not p['fixed']]
        bounds = [min(p['screen'][0] for p in cub)-4, min(p['screen'][1] for p in cub)-4,
                  max(p['screen'][0]+p['size'] for p in cub)+4,
                  max(p['screen'][1]+p['size'] for p in cub)+4]
        changes = []
        for a, b in (('native', 'palette'), ('frames', 'both')):
            changed = [i for i, (x, y) in enumerate(zip(pictures[a][2], pictures[b][2])) if x != y]
            assert changed, (level, 'Palette choice was invisible', a, b)
            assert all(bounds[0] <= i%640/2-32 < bounds[2] and bounds[1] <= i//640/2 < bounds[3]
                       for i in changed), (level, 'Palette escaped cub bounds', bounds)
            changes.append(len(changed))
        reference_name = f'{level}-continuous'
        reference, _ = run(reference_name, 'sdl', 'both', save_frame+1,
                           ['--load', state, '--input-polled', suffix], True)
        for profile in ('native', 'both'):
            saved = out/f'{level}-{profile}-moving.state'
            _, used = run(f'{level}-save-{profile}', 'sdl', profile, save_frame,
                          ['--load', state, '--input-polled', suffix, '--save-at', save_frame, saved])
            after = out/f'{level}-{profile}-after.polled.tape'
            after.write_bytes(suffix.read_bytes()[used*2:])
            name = f'{level}-loaded-{profile}'
            actual, _ = run(name, 'sdl', 'both', save_frame+1,
                            ['--load', saved, '--input-polled', after], True)
            assert actual == reference and pixels(out/(name+'.png')) == pixels(out/(reference_name+'.png'))
            assert json.loads((out/(name+'.json')).read_text()) == json.loads((out/(reference_name+'.json')).read_text())
        results[str(level)] = {'runs': rows, 'independent_palette_changed_pixels': changes,
                               'moving_first_loaded_fields_identical': ['native', 'both']}
        print('Level', level, 'independent cub art/palette, AOT/LLE and moving saves PASS', flush=True)
    # The global cub choice must not replace the adult player in a later scene.
    adult = {}
    for profile in ('native', 'frames'):
        name = 'adult-'+profile
        value, _ = run(name, 'sdl', profile, 2300, ['--practice-level', 6], True)
        coverage = json.loads((out/(name+'-coverage.json')).read_text())
        assert coverage['seen_by_role']['cub'] == 0
        adult[profile] = value
    assert adult['native'] == adult['frames'] and pixels(out/'adult-native.png') == pixels(out/'adult-frames.png')
    (out/('adult-report.json' if args.adult_only else 'report.json')).write_text(json.dumps({'result': 'PASS', 'scope': __doc__, 'levels': results,
                                             'unsupported_adult_window_and_guest_unchanged': True,
                                             'unmapped_poses_use_native_art': True}, indent=2)+'\n')
    print('Unsupported adult scene: native window and guest identical PASS', flush=True)


if __name__ == '__main__':
    main()
