"""Review shared defeat-puff art using paired original action phases and palettes.

The old catalog classified these shared effects as porcupines. Live predecessor
and action observations establish the shared handler independently of that name.
"""
import json
import struct
import sys
from collections import Counter
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]/'.tools/pythonlibs'))
from PIL import Image, ImageDraw
from pride_sprite_catalog import ROOT, read_rom, pride_snes_graphics, snes_frame, md_frame, bitmap

PAIRS = list(zip((0xc2f35f, 0xc2f396, 0xc2f3e1, 0xc2f428, 0xc2f47f, 0xc2f4ca, 0xc2f50d, 0xc2f550),
                 (0xb4fec, 0xb5014, 0xb505c, 0xb50d4, 0xb514c, 0xb51e4, 0xb527c, 0xb52f4)))


def main():
    snes = pride_snes_graphics(read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    source = ROOT/'build/lizard-defeat-original'
    native = json.loads((source/'native.json').read_text())
    external = json.loads((source/'md.json').read_text())
    metadata = {int(r['snes'], 16): r for r in json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']}
    observations = []
    for report in (native, external):
        rows = [r for e in report['entries'] for r in report['observations']
                if r['actor'] == e['actor'] and e['frame'] <= r['frame'] < e['frame']+32]
        assert len(rows) == 64 and all(r['palette'] == 0 for r in rows)
        observations.append(rows)
    raw = struct.unpack_from('>16H', md, 0x1d78aa)
    expected = [(c >> 1 & 7) | (c >> 5 & 7) << 3 | (c >> 9 & 7) << 6 for c in raw]
    assert all(r['display_enabled'] and r['level_register'] == 1 and r['palette_rgb9'][1:] == expected[1:]
               for r in observations[1]), 'Original live puff palette differs from shared palette0'
    palettes = [list(struct.unpack_from('<16H', snes, 0x7b93)),
                [sum((((c >> s & 7)*4 + ((c >> s & 7) >> 2)) << (i*5)) for i, s in enumerate((1, 5, 9))) for c in raw]]
    def points(image):
        x, y, w, h, data = image
        return {(x+i%w, y+i//w): c for i, c in enumerate(data) if c}
    native_images = [bitmap(snes, snes_frame(snes, p & 0x3fffff), False, with_origin=True) for p, _ in PAIRS]
    md_images = [bitmap(md, md_frame(md, q), True, with_origin=True) for _, q in PAIRS]
    sheet = Image.new('RGB', (640, 120*len(PAIRS)), (28, 28, 32))
    draw = ImageDraw.Draw(sheet)
    rows = []
    for phase, ((p, q), a, b) in enumerate(zip(PAIRS, native_images, md_images)):
        pair = metadata[p]
        assert pair['role'] == 'defeat_puff' and pair['native_palette'] == pair['md_palette'] == 0 and int(pair['md'], 16) == q
        pa, pb = points(a), points(b)
        ranking = sorted((len(pa.keys() ^ points(image).keys()), other) for (_, other), image in zip(PAIRS, md_images))
        assert ranking[0][1] == q, 'Paired phase has a closer distinct effect silhouette'
        phases = [[r for r in observed if r['pose'] == pose] for observed, pose in zip(observations, (p, q))]
        assert all(len(r) == 8 for r in phases), 'Each phase must be observed for4 updates in each of2 actions'
        rows.append({'snes': p, 'md': q, 'role': 'defeat_puff', 'native_origin_size': a[:4],
                     'md_origin_size': b[:4], 'mask_difference': len(pa.keys() ^ pb.keys()),
                     'indexed_difference': sum(pa.get(xy) != pb.get(xy) for xy in pa.keys() | pb.keys()),
                     'nearest_other_phase_mask_difference': ranking[1][0], 'observed_updates_per_version': 8})
        for column, (label, image, colors) in enumerate(((f'SNES {p:06x}', a, palettes[0]), (f'MD {q:06x}', b, palettes[1]))):
            x, y, w, h, data = image
            draw.text((column*320+8, phase*120+4), f'{phase+1}: {label} origin {x},{y}', fill='white')
            pic = Image.new('RGB', (w, h), (28, 28, 32))
            for i, pixel in enumerate(data):
                if pixel:
                    color = colors[pixel]
                    pic.putpixel((i%w, i//w), tuple((color >> (s*5) & 31)*255//31 for s in range(3)))
            sheet.paste(pic.resize((w*2, h*2), Image.Resampling.NEAREST), (column*320+64, phase*120+25))
    out = ROOT/'build/defeat-puff-art'
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out/'review.png')
    report = {'result': 'PASS', 'scope': __doc__, 'pairs': rows, 'live_md_palette_checks': 64,
              'original_native_palette_bank_checks': 64, 'not_exclusive_to_porcupines': True,
              'source_choices_independent_of_audio_and_enemy_art': True}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Shared defeat puff: eight observed original phases and live palette0 PASS', flush=True)


if __name__ == '__main__':
    main()
