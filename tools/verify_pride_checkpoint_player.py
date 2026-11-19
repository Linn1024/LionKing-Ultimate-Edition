"""Verify checkpoint-only source mixtures in actual ordinary Windows gameplay."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from pride_sprite_catalog import bitmap, snes_frame, md_frame
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=int, default=5400)
    parser.add_argument('--collection', action='store_true')
    parser.add_argument('--full-matrix', action='store_true',help='All frame/palette sources during collection')
    parser.add_argument('--pose',type=lambda s:int(s,0),default=0xc456de,
                        choices=(0xc456de,0xc2fde1,0xc2fe18))
    args = parser.parse_args()
    out = ROOT / f'build/pride-checkpoint-player/windows-{args.frame}'
    out.mkdir(exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text('{"result":"RUNNING"}\n')
    candidate = ROOT/'engine/build-win/tlk_sdl.exe'
    baseline = ROOT/'build/pride-checkpoint-player/baseline-sdl.exe'
    assert digest(baseline) == 'd49a9374c73795e5885e7e0e7f0977bd172222e5c8a813e3006982c51719788b'
    candidate_sha = digest(candidate)
    source_paths = [Path(__file__), *[ROOT/p for p in (
        'engine/runner/tlk_wide.c', 'engine/runner/tlk_wide.h', 'engine/runner/tlk_resources.c',
        'engine/runner/tlk_resources.h', 'engine/runner/tlk_checkpoint_role.h',
        'engine/runner/tlk_checkpoint_art.c', 'engine/runner/tlk_checkpoint_art.h',
        'engine/runner/tlk_revival_art.c', 'engine/runner/tlk_death_scene.c',
        'engine/runner/sdl_main.c', 'engine/runner/tlk_menu_imgui.cpp', 'engine/CMakeLists.txt')]]
    sources = {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in source_paths}
    snes = (ROOT/'Lion King, The (USA).sfc').read_bytes()
    md = (ROOT/'Lion King, The (World).md').read_bytes()
    counterpart = {0xc456de:0x973b6,0xc2fde1:0x977c6,0xc2fe18:0x977fe}[args.pose]
    art = [bitmap(snes, snes_frame(snes, args.pose&0x3fffff), False, with_origin=True),
           bitmap(md, md_frame(md, counterpart), True, with_origin=True)]
    native_palette = [int.from_bytes(snes[0x7b93+i*2:0x7b95+i*2], 'little') for i in range(16)]
    md_palette = []
    for i in range(16):
        raw = int.from_bytes(md[0x1d78aa+i*2:0x1d78ac+i*2], 'big')
        md_palette.append(sum((((raw>>s)&7)*4+(((raw>>s)&7)>>2))<<o for s,o in ((1,0),(5,5),(9,10))))
    palettes = [native_palette, md_palette]
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    cases = {}
    for width in (256, 320):
        common = 'schema = 1\ngame = snes\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n'

        def run(name, exe, frames, palette, mode='aot', sibling=False):
            folder = out/f'{width}-{name}'
            folder.mkdir(exist_ok=True)
            profile = folder/'resources.ini'
            text = common+'graphics.sprites.checkpoints.frames = '+('md' if frames else 'snes')+'\n'
            text += 'graphics.sprites.checkpoints.palette = '+('md' if palette else 'snes')+'\n'
            # The baseline predates these IDs; it uses the unchanged native profile.
            if exe == baseline:
                text = common
            if sibling:
                text += 'graphics.sprites.simba.cub.palette = md\ngraphics.hud.palette = md\n'
            profile.write_text(text)
            cmd = [exe, '--rom', ROOT/'Lion King, The (USA).sfc', '--md-rom', ROOT/'Lion King, The (World).md',
                   '--resource-profile', profile, '--config', config, '--frames', str(args.frame),
                   '--input-polled', ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                   '--no-pace', '--no-audio', '--no-record', '--dump-window', folder/'window.png',
                   '--dump-png', folder/'guest.png', '--dump-scene', folder/'scene.json',
                   '--wav', folder/'audio.wav', '--wav-seconds', '100']
            if mode == 'lle':
                cmd.append('--lle')
            if not args.collection and name == 'both-aot':
                cmd += ['--save-at', '5300', folder/'checkpoint.state']
            capture = dict(binary_sha256=digest(exe), source_sha256=sources,
                           profile_sha256=digest(profile), execution_completed=False)
            (folder/'capture.json').write_text(json.dumps(capture, indent=2)+'\n')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str, cmd)), cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
            assert digest(exe) == capture['binary_sha256']
            for file, sha in sources.items():
                assert digest(ROOT/file) == sha, file
            capture['execution_completed'] = True
            (folder/'capture.json').write_text(json.dumps(capture, indent=2)+'\n')
            picture = pixels(folder/'window.png')
            assert picture[:2] == (width*2, 448)
            scene = json.loads((folder/'scene.json').read_text())
            assert scene['level'] == 0 and scene['stage_detected']
            assert scene['latched_gameplay']['lives'] == (8 if args.collection else 7)
            return folder, picture[2], scene

        base_folder, base_picture, base_scene = run('baseline', baseline, 0, 0)
        combinations = [('both',1,1)] if args.collection and not args.full_matrix else [('native',0,0), ('frames',1,0), ('palette',0,1), ('both',1,1)]
        combinations = [(name, f, p, mode, False) for name,f,p in combinations for mode in ('aot','lle')]
        if not args.collection:
            combinations.append(('siblings',0,0,'aot',True))
        for name, frames, palette, mode, sibling in combinations:
            folder, picture, scene = run(name+'-'+mode, candidate, frames, palette, mode, sibling)
            assert hashes(folder/'run.log') == hashes(base_folder/'run.log')
            assert (folder/'guest.png').read_bytes() == (base_folder/'guest.png').read_bytes()
            assert wav_data(folder/'audio.wav') == wav_data(base_folder/'audio.wav')
            heads = [p for p in scene['pieces'] if p['pose'] == args.pose and p['position_pointer'] != 0xb21b]
            assert heads, (name, width, 'No checkpoint head in captured scene')
            origins = {(p['screen'][0]-p['local'][0],p['screen'][1]-p['local'][1]) for p in heads}
            assert len(origins) == 1, origins
            ox, oy = origins.pop()
            ox += (width-256)//2
            left, top, w, h, indices = art[frames]
            expected = list(base_picture)
            checked = occluded = 0
            source_images = {}
            head_slots = {p['slot'] for p in heads}
            def covered_by_prior_sprite(dx,dy):
                # Native OBJ ordering is by physical slot, independently of
                # OBJ/BG priority. The moving hero overlaps the touched head.
                for piece in scene['pieces']:
                    if not piece['kept'] or piece['slot'] >= min(head_slots):
                        continue
                    px = dx-(piece['screen'][0]+(width-256)//2)
                    py = dy-piece['screen'][1]
                    size = piece['size']
                    if not (0 <= px < size and 0 <= py < size):
                        continue
                    pose = piece['pose']
                    if pose not in source_images:
                        source_images[pose] = bitmap(snes,snes_frame(snes,pose&0x3fffff),False,with_origin=True)
                    sx = piece['local'][0]+(size-1-px if piece['attributes']&0x4000 else px)
                    sy = piece['local'][1]+(size-1-py if piece['attributes']&0x8000 else py)
                    ix,iy,iw,ih,indices = source_images[pose]
                    if 0 <= sx-ix < iw and 0 <= sy-iy < ih and indices[(sy-iy)*iw+sx-ix]:
                        return True
                return False
            for y in range(h):
                for x in range(w):
                    index = indices[y*w+x]
                    dx, dy = ox+left+x, oy+top+y
                    if not index or not (0 <= dx < width and 0 <= dy < 224):
                        continue
                    if covered_by_prior_sprite(dx,dy):
                        occluded += 1
                        continue
                    color = palettes[palette][index]
                    rgb = tuple(((color>>s)&31)*8+((color>>s)&31)//4 for s in (0,5,10))
                    for yy in (dy*2,dy*2+1):
                        for xx in (dx*2,dx*2+1):
                            at = yy*width*2+xx
                            expected[at] = rgb
                            assert picture[at] == rgb, (name, mode, width, dx, dy)
                    checked += 1
            assert checked > 0
            stats = scene['checkpoint_adapter']
            if frames or palette:
                assert stats['pixels'] > 0 and stats['fallback_pixels'] == 0
            else:
                assert stats['pixels'] == 0
            if not sibling:
                assert picture == expected, (name, mode, width, 'Changes outside original checkpoint pixels')
            else:
                assert picture != base_picture, 'Sibling source changes did not run'
            key = f'{width}-{name}-{mode}'
            cases[key] = dict(original_head_pixels=checked,occluded_head_pixels=occluded,guest_and_native_pcm_exact=True,
                full_window_matches_original_head_only_change=not sibling,
                checkpoint_stays_native_with_md_siblings=sibling, adapter=stats,
                artifacts_sha256={p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()})
            print(key, checked, 'original head pixels; guest/PCM and actual Windows source isolation PASS', flush=True)
    report = dict(result='PASS', scope=__doc__, candidate_sha256=candidate_sha,
        baseline_sha256=digest(baseline), frame=args.frame, collection=args.collection, pose=args.pose,
        full_matrix=args.full_matrix,cases=cases,
        source_sha256=sources, ordinary_inputs=True, practice_or_guest_edits=False,
        full_first_level_fidelity_complete=False)
    report_path.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
