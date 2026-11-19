"""Check shared cub art against original second/third-level and Exile MD captures.

Checks pose records and indexed artwork, not animation timing or full-core sync.
Original captures and decoded pixels remain ignored research artifacts.
"""
import argparse
import hashlib
import json
import struct
from audit_scenes import ROOT, read_rom
from pride_sprite_catalog import bitmap, md_frame, snes_frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exile', action='store_true', help='Verify unforced BizHawk Exile captures')
    exile = parser.parse_args().exile
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    snes = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    source = ROOT/('build/md-exile-art-reference' if exile else 'build/md-next-levels-replay')
    frames = {} if exile else {r['frame']: r for r in json.loads((source/'frames.json').read_text())}
    catalog = json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    pairs = catalog['exact_matches'] + catalog['pixel_art_variants']
    samples = []
    for frame in ((24500, 25000, 25500) if exile else (6000, 8000, 10000, 12000, 14000, 16000, 18000)):
        directory = source/f'capture-{frame}'
        ram = (source/f'{frame}-68K RAM.bin' if exile else directory/'work_ram.bin').read_bytes()
        word = lambda a: struct.unpack_from('>H' if exile else '<H', ram, a & 65535)[0]
        camera = word(0xcd36)
        player = word(camera+0x24)
        draw = word(player+12)
        assert all(0x8000 <= p <= 0xff80 for p in (camera, player, draw))
        pose = (word(draw+10) << 16 | word(draw+12)) & 0xffffff
        level = 4 if exile else 1 if frame <= 12000 else 2
        assert word(0xccce) == level+1
        if exile:
            assert (word(0xcd2e)<<16 | word(0xcd30)) == 0x1ff34e
        else:
            assert frames[frame]['level'] == level
            assert (directory/'reg.bin').read_bytes()[1] & 64
        assert (word(draw+8) >> 13 & 3) == 0
        cram = struct.unpack('>64H' if exile else '<64H',
                             (source/f'{frame}-CRAM.bin' if exile else directory/'cram.bin').read_bytes())
        expected = []
        for color in struct.unpack_from('>16H', md, 0x1d78aa):
            expected.append(color if exile else (color >> 1 & 7) | (color >> 5 & 7) << 3 | (color >> 9 & 7) << 6)
        assert list(cram[1:16]) == expected[1:16], 'Cub palette was repurposed or flashing'
        image = bitmap(md, md_frame(md, pose), True)
        # Check literal original records again, rather than trusting catalog labels.
        matches = []
        for pair in pairs:
            if pose not in [int(q, 16) for q in pair['md']]:
                continue
            native = int(pair['snes'], 16)
            if native >= len(snes):
                continue
            pieces = snes_frame(snes, native)
            if not pieces:
                continue
            native_image = bitmap(snes, pieces, False)
            if native_image == image:
                matches.append({'snes': native, 'different_indexed_points': 0})
            elif 'different_indexed_points' in pair:
                # Retain the already reviewed tiny art variants, including the
                # single additional pixel in the wall-climbing pose at 16000.
                a = bitmap(snes, pieces, False, with_origin=True)
                b = bitmap(md, md_frame(md, pose), True, with_origin=True)
                def points(v):
                    x, y, w, h, data = v
                    return {(x+i%w, y+i//w, c) for i, c in enumerate(data) if c}
                difference = len(points(a) ^ points(b))
                assert difference == pair['different_indexed_points'] <= 8
                matches.append({'snes': native, 'different_indexed_points': difference})
        assert matches, ('Original cub pose has no reviewed shared ROM art', frame, hex(pose))
        samples.append({'frame': frame, 'level': level, 'original_level_register': word(0xccce), 'md_pose': pose,
                        'native_candidates': matches, 'palette_bank': 0,
                        'wram_sha256': hashlib.sha256(ram).hexdigest()})
    out = ROOT/('build/exile-cub-reference' if exile else 'build/next-cub-reference')
    out.mkdir(parents=True, exist_ok=True)
    report = {'result': 'PASS', 'scope': __doc__, 'original_samples': samples,
              'animation_timing_verified': False, 'full_core_synchronization_verified': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Original cub:', len(samples), 'live poses/palettes and reviewed ROM art PASS', flush=True)


if __name__ == '__main__':
    main()
