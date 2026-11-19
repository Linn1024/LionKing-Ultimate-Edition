"""Compare presented native widgets with original CPU-built font pixels."""
import array
import csv
import hashlib
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from analyze_pride_scene_oam import records


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / 'build/pride-prepared-widget-pixels'
    output.mkdir(exist_ok=True)
    inputs = [Path(__file__), ROOT / 'build/pride-native-hud-oracle/report.json',
              ROOT / 'build/pride-native-hud-oracle/original-fonts.bin',
              ROOT / 'build/pride-scene-oam-audit/native/native-oam.bin',
              ROOT / 'tools/analyze_pride_scene_oam.py',
              ROOT / 'engine/runner/sdl_main.c']
    oracle = json.loads(inputs[1].read_text())
    assert oracle['result'] == 'PASS' and oracle['ordinary_checkpoint_widget_targets_exact']
    raw = inputs[2].read_bytes()
    fonts = {struct.unpack_from('<II', raw, at): raw[at+520:at+1032]
             for at in range(8, len(raw), 1032)}
    original = next(r for r in records(inputs[3]) if r['head'][1] == 268)
    cases = {}
    for host in ('headless', 'sdl'):
        for width in (320, 256):
            parent = ROOT / f'build/pride-scene-render-prepared-{host}-{width}-5400'
            report_path = parent / 'report.json'
            report = json.loads(report_path.read_text())
            assert report['result'] == 'OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN', report_path
            assert report['prepared_objects']
            inputs.append(report_path)
            for profile in ('native', 'frames', 'palette'):
                folder = parent / (profile + '-owned')
                trace = folder / 'render-owned.rgb'
                events = folder / 'prepared-objects.csv'
                inputs.extend((trace, events))
                rows = {int(r['age']): r for r in csv.DictReader(events.open())}
                assert all(int(rows[age]['source_age']) == 268 and int(rows[age]['staged_pieces']) == 25
                           for age in range(270, 298))
                assert all(int(rows[age]['staged_pieces']) == 0 for age in range(298, max(rows)+1))
                run = report['runs'][profile + '-owned']
                assert digest(trace) == run['artifacts_sha256']['render-owned.rgb']
                assert digest(events) == run['artifacts_sha256']['prepared-objects.csv']
                count = width * 224
                size = 56 + count * 12
                compared = 0
                with trace.open('rb') as f:
                    assert f.read(16) == b'PRDRGB01' + struct.pack('<II', width, 224)
                    for age in range(273, run['release_age']+1):
                        f.seek(16 + age * size)
                        record = f.read(size)
                        assert struct.unpack_from('<I', record)[0] == age
                        actual = array.array('I')
                        actual.frombytes(record[-count*4:])
                        for kind, maximum, origin in ((0, 24, 16), (1, 6, 200)):
                            piece = next(p for p in original['pieces'] if p[13] == kind)
                            assert piece[1] == 14 and piece[4] == 16 and piece[11] == 0
                            font = fonts[kind, maximum]
                            # Headless --wide defaults to centered HUD; SDL's
                            # default widescreen_hud=edges anchors left/right.
                            origin += (width-256)*kind if host == 'sdl' else (width-256)//2
                            for y in range(16):
                                palette = struct.unpack('<256H', original['raster'][14+y][2])
                                for x in range(min(64, width-origin)):
                                    at = (y//8)*256 + (x//8)*32 + (y&7)*2
                                    bit = 7-(x&7)
                                    index = sum(((font[at+(b//2)*16+b%2] >> bit)&1) << b for b in range(4))
                                    if not index:
                                        continue
                                    color = palette[128+((piece[2]>>9)&7)*16+index]
                                    # Declared native five-bit hybrid fade; this
                                    # does not claim original SNES fade timing.
                                    components = [min((color>>shift)&31, (age-270)//3*4)
                                                  for shift in (0, 5, 10)]
                                    red, green, blue = [v*8+v//4 for v in components]
                                    expected = red<<16 | green<<8 | blue
                                    assert actual[(14+y)*width+origin+x] == expected, (host, width, profile, age, kind, x, y)
                                    compared += 1
                cases[f'{host}-{width}-{profile}'] = dict(first_age=273, last_age=run['release_age'],
                    independently_compared_opaque_widget_pixels=compared)
                print(host, width, profile, compared, 'original native widget pixels PASS', flush=True)
    result = dict(result='PASS', scope=__doc__, cases=cases,
        independently_compared_opaque_widget_pixels=sum(r['independently_compared_opaque_widget_pixels'] for r in cases.values()),
        native_health6_and_roar24_only=True, original_md_widget_parity_verified=False,
        headless_hud_placement='centered', sdl_hud_placement='edges',
        full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in inputs})
    (output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Twelve native-HUD graphics mixtures: original CPU font pixels and staged-object interval exact PASS', flush=True)


if __name__ == '__main__':
    main()
