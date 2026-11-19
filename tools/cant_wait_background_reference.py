"""Export original second-level plane-B tokens and palette fade fixtures.

Ordinary power-on replay only. Keep all cartridge-derived output under build/.
No guest RAM/register/cartridge writes or loaded states are used. This exports
one plane before sprites/priority, not a complete original or mixed screenshot.
Run with .tools/python32/python.exe.
"""
import collections
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'build/md-next-levels-replay'
    out = ROOT/'build/cant-wait-renderer'
    out.mkdir(parents=True, exist_ok=True)
    report_path = out/'reference.json'
    report_path.write_text(json.dumps({'result': 'RUNNING'})+'\n')
    rom_hash = digest(ROOT/'Lion King, The (World).md')
    assert rom_hash == 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    rows = json.loads((source/'frames.json').read_text())
    audit = {r['frame']: r for r in json.loads((source/'scene-backgrounds.json').read_text())}
    frames = (5013, 5040, 5100, 5200, 6000, 8000, 10000, 12000)
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1):
        game.core.retro_set_controller_port_device(port, 513)
    snapshots = 0
    samples = []
    word = lambda data, at: struct.unpack_from('<H', data, at)[0]
    try:
        with (out/'original-pixels.bin').open('wb') as output:
            output.write(b'CWAITBG1'+struct.pack('<I', len(frames)))
            for row in rows:
                frame = row['frame']
                game.step(row['pad'])
                snapshot = source/f'{frame:05d}-wram.bin'
                if frame % 100 == 1 and snapshot.exists():
                    assert bytes(game.work_ram) == snapshot.read_bytes(), ('Original replay changed', frame)
                    snapshots += 1
                if frame in frames:
                    observation = audit[frame]
                    prior = audit[frame-1]
                    assert observation['level'] == 1 and observation['display_enabled']
                    vram, reg, vs = bytes(game.vram), bytes(game.reg), bytes(game.vsram)
                    assert reg[11] == 3 and reg[16] == 1 and word(vs, 2) == 0
                    assert not observation['name_errors'] and observation['base_tiles_match']
                    table = (reg[4]&7)<<13
                    hbase = (reg[13]&63)<<10
                    tokens = []
                    for y in range(224):
                        scroll = (-word(vram, hbase+4*y+2))&1023
                        for x in range(320):
                            wx = (x+scroll)&511
                            tile = word(vram, table+(y//8*64+wx//8)*2)
                            xx, yy = wx&7, y&7
                            if tile&0x800: xx = 7-xx
                            if tile&0x1000: yy = 7-yy
                            packed = vram[((tile&2047)*32+yy*4+xx//2)^1]
                            pixel = (packed>>(0 if xx&1 else 4))&15
                            tokens.append(((11 if tile&0x8000 else 7)<<12)|0x900|((tile>>13)&3)*16|pixel if pixel else 0)
                    # Original compact CRAM -> cartridge word channel positions.
                    palette = [((c&7)<<1)|(((c>>3)&7)<<5)|(((c>>6)&7)<<9)
                               for c in struct.unpack('<64H', bytes(game.cram))]
                    output.write(struct.pack('<5I64H', frame, prior['camera_x'], prior['offset_x'], 320, 224, *palette))
                    output.write(struct.pack('<'+'H'*len(tokens), *tokens))
                    picture = out/f'{frame}.png'
                    png(picture, *game.image)
                    if (source/f'capture-{frame}/screen.png').exists():
                        assert picture.read_bytes() == (source/f'capture-{frame}/screen.png').read_bytes()
                    samples.append({'frame': frame, 'camera_x': prior['camera_x'], 'wrap_x': prior['offset_x'],
                                    'palette_variants': observation['normal_background_palette_variants'],
                                    'picture_sha256': digest(picture), 'pixels': len(tokens)})
                game.samples.clear()
                if frame % 2000 == 0:
                    print('Original second-level pixel reference', frame, flush=True)
                if frame == frames[-1]:
                    break
    finally:
        game.close()
    assert len(samples) == len(frames) and snapshots > 100
    # Independently recorded writes from original 18D816, including all 100
    # software colors; these need not equal the displayed CRAM on that field.
    palette_report_path = ROOT/'build/cant-wait-palette/report.json'
    palette_report = json.loads(palette_report_path.read_text())
    writers_path = palette_report_path.parent/'writers.csv'
    assert palette_report['writers_csv_sha256'] == digest(writers_path)
    assert palette_report['input_reference_sha256'] == digest(source/'frames.json')
    passes = collections.defaultdict(list)
    for row in csv.DictReader(writers_path.open()):
        if row['type'] == '4' and row['pc'] == '18d816':
            passes[int(row['frame'])].append(row)
    with (out/'original-fades.bin').open('wb') as output:
        output.write(b'CWFADE01'+struct.pack('<I', len(passes)))
        for frame, writes in passes.items():
            assert [int(r['address'], 16) for r in writes] == list(range(0xff845c, 0xff8524, 2))
            assert [int(r['a0'], 16)-2 for r in writes] == list(range(0x1ea684, 0x1ea74c, 2))
            output.write(struct.pack('<I200H', frame, *[int(r['before'], 16) for r in writes],
                                     *[int(r['value'], 16) for r in writes]))
    report = {'result': 'PASS', 'scope': __doc__, 'samples': samples,
              'rom_sha256': rom_hash,
              'unchanged_wram_snapshots': snapshots, 'pixels': sum(r['pixels'] for r in samples),
              'palette_passes': len(passes), 'palette_writes': sum(map(len, passes.values())),
              'frames_source_sha256': digest(source/'frames.json'),
              'core_sha256': digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
              'palette_report_sha256': digest(palette_report_path), 'writers_sha256': digest(writers_path),
              'pixel_fixture_sha256': digest(out/'original-pixels.bin'),
              'fade_fixture_sha256': digest(out/'original-fades.bin'),
              'exporter_sha256': digest(Path(__file__)), 'mixed_background_enabled': False}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Original second-level reference PASS:', report['pixels'], 'pixels,', report['palette_writes'], 'fade writes', flush=True)


if __name__ == '__main__':
    main()
