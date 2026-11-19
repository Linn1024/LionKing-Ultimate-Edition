"""Review the two original HUD popup streams and their visible artwork.

This is artwork evidence, not a production renderer or timing adaptation.
"""
import csv
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'.tools/pythonlibs'))
from PIL import Image, ImageDraw
from pride_sprite_catalog import ROOT, read_rom, pride_snes_graphics, snes_frame, md_frame, bitmap


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/pride-popup-art-review'
    out.mkdir(exist_ok=True)
    assert not (out/'report.json').exists(), 'Keep completed reviews immutable'
    capture = ROOT/'build/pride-popup-original'
    report_path = capture/'report.json'
    capture_report = json.loads(report_path.read_text())
    for name, sha in capture_report['artifacts_sha256'].items():
        assert digest(capture/name)==sha
    calls = list(csv.DictReader((capture/'calls.csv').open()))
    executed = {(int(r['field']), int(r['actor'], 16)) for r in calls
                if r['callback']=='190048' and r['action']=='18ffe6'}
    # Pool slots retain the retired action and pose. Never call those active.
    samples = [r for r in capture_report['samples']
               if (r['field'], r['actor']) in executed]
    raw = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    snes = pride_snes_graphics(raw)
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    streams = []
    # Native C239FE is an animation installer; its immediate points to C23A1E.
    assert raw[0x239fe:0x23a01] == bytes.fromhex('a91e3a')
    for rom, start, endian in ((raw, 0x23a1e, 'little'), (md, 0x937ee, 'big')):
        stream = []
        for i in range(40):
            at = start+i*4
            delay, pose = rom[at], int.from_bytes(rom[at+1:at+4], endian)
            if delay==255:
                break
            stream.append(dict(delay=delay, pose=pose))
        else:
            raise AssertionError('Missing original stream terminator')
        streams.append(stream)
    assert {r['pose'] for r in samples} == {r['pose'] for r in streams[1]}
    palettes = [list(struct.unpack_from('<16H', raw, 0x7b93)),
                [sum((((c>>s&7)*4+((c>>s&7)>>2))<<(i*5)) for i,s in enumerate((1,5,9)))
                 for c in struct.unpack_from('>16H', md, 0x1d78aa)]]
    sheet = Image.new('RGB', (720, 80*max(map(len, streams))), (28,28,32))
    draw = ImageDraw.Draw(sheet)
    decoded = []
    for column, (rom, stream) in enumerate(zip((snes, md), streams)):
        images = []
        for index, row in enumerate(stream):
            p = row['pose'] & 0x3fffff
            pieces = md_frame(rom,p) if column else snes_frame(rom,p)
            assert pieces, hex(p)
            image = bitmap(rom,pieces,bool(column),with_origin=True)
            images.append(image)
            x,y,w,h,data = image
            pic = Image.new('RGB',(w,h),(28,28,32))
            for i,c in enumerate(data):
                if c:
                    color = palettes[column][c]
                    pic.putpixel((i%w,i//w), tuple((color>>(n*5)&31)*255//31 for n in range(3)))
            label = f'{"MD" if column else "SNES"} {row["pose"]:06x} delay {row["delay"]}, origin {x},{y}'
            draw.text((column*360+5,index*80+3), label,fill='white')
            sheet.paste(pic.resize((w*3,h*3),Image.Resampling.NEAREST),(column*360+120,index*80+21))
        decoded.append(images)
    sheet.save(out/'review.png')
    # Anchored indexed equality includes shape, origin and colour indices.
    matches = [{**row, 'exact_md_phases':[i for i,b in enumerate(decoded[1]) if a==b],
                'origin_size':a[:4]} for row,a in zip(streams[0],decoded[0])]
    paths = [Path(__file__), ROOT/'tools/pride_sprite_catalog.py', report_path,
             ROOT/'tools/capture_pride_popup_art.py']
    result = dict(result='ORIGINAL_POPUP_STREAMS_DECODED',
                  native_stream=streams[0], md_stream=streams[1],
                  native_phase_matches=matches,
                  raw_pool_samples=len(capture_report['samples']),
                  samples_with_executed_callback=samples,
                  stale_pool_samples_excluded=len(capture_report['samples'])-len(samples),
                  production_mapping_enabled=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={'review.png':digest(out/'review.png')})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(streams[0]),'native phases;',len(streams[1]),'MD phases;',
          result['stale_pool_samples_excluded'],'stale samples excluded',flush=True)


if __name__=='__main__':
    main()
