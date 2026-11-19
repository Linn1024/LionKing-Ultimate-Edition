"""Verify live-cell MD terrain attributes on an ordinary Pride controller route.

No guest map, actor, position or health edits. Original collision dictionaries
remain unchanged; changed-cell fallback and positional aliases have C unit gates.
"""
import csv
import importlib.util
import json
import os
import struct
import subprocess
from audit_scenes import ROOT, read_rom
from verify_windows import hashes


def main():
    out = ROOT / 'build/pride-terrain-runtime'
    out.mkdir(parents=True, exist_ok=True)
    snes = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    spec = importlib.util.spec_from_file_location('terrain_lz', ROOT / 'engine/tools/re/decompress.py')
    lz = importlib.util.module_from_spec(spec); spec.loader.exec_module(lz)
    ptr = lambda offset: int.from_bytes(snes[0x387+offset:0x38a+offset], 'little') & 0x3fffff
    sm = lz.decompress(snes, ptr(9))[0]
    sc = lz.decompress(snes, ptr(0))[0]
    mc = int.from_bytes(md[0x1cfdb8:0x1cfdbc], 'big')
    mm = lz.decompress(md, int.from_bytes(md[0x1cfdc4:0x1cfdc8], 'big'))[0]
    expected = []
    for i in range(8000):
        sw, mw = struct.unpack_from('<H', sm, i*2)[0], struct.unpack_from('>H', mm, i*2)[0]
        expected.append((sw, sc[(sw & 0xfff8)//2+2], md[mc+(mw & 0xfff8)//2+2]))
    baseline = json.loads((ROOT / 'build/pride-baseline/report.json').read_text())['hashes']
    results = {}; traces = {}
    for name in ('native', 'md-aot', 'md-lle', 'md256'):
        folder = out / name; folder.mkdir(exist_ok=True)
        profile = folder / 'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('snes' if name=='md256' else 'md')+'\n' +
                           ('gameplay.levels.pride_lands.contacts = md\n' if name != 'native' else ''))
        env = os.environ.copy(); env['TLK_TERRAIN_TRACE'] = str(folder / 'terrain.csv')
        env.update(TLK_WRAM_DUMP='1000', TLK_WRAM_DIR=str(folder))
        cmd = [str(ROOT / 'engine/build-win/tlk_headless.exe'), '--rom', str(ROOT / 'Lion King, The (USA).sfc'),
               '--md-rom', str(ROOT / 'Lion King, The (World).md'), '--resource-profile', str(profile),
               '--asset-cache', str(ROOT / 'game-data/scenes-v1.cache'), '--frames', '5000',
               '--input-polled', str(ROOT / 'engine/tapes/allbugsF.read.tape'), '--ram-log', str(folder / 'game.ram')]
        if name == 'md-lle': cmd.append('--lle')
        log = folder / 'game.log'
        with log.open('wb') as stream:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT,
                           check=True, timeout=300)
        assert 'Saved resource profile loaded' in log.read_text(), name + ' source profile rejected'
        assert 'resource_cache=loaded' in log.read_text(), 'Cached install path not exercised'
        ram = (folder / 'hl_wram_1000.bin').read_bytes()
        assert struct.unpack_from('<H', ram, 0xdf)[0] == 0x387, 'Wrong fixture scene'
        collision_at = int.from_bytes(ram[0xef:0xf2], 'little') - 0x7e0000
        assert ram[collision_at:collision_at+len(sc)] == sc, 'Shared collision dictionary was changed'
        if name != 'native':
            rows = list(csv.DictReader((folder / 'terrain.csv').open()))
            assert rows, 'No contact substitutions observed'
            normalized = []
            for row in rows:
                cell = int(row['cell']); word = int(row['live_word'], 16)
                assert (word, int(row['native']), int(row['md'])) == expected[cell], row
                assert int(row['map_address'], 16) == 0x7f0000+cell*2, row
                normalized.append((int(row['pc'], 16) & 65535, cell, int(row['native']), int(row['md'])))
            assert any(a != b for _, _, a, b in normalized), 'Changed contact cells were not exercised'
            traces[name] = normalized
        rows = [line.split() for line in (folder / 'game.ram').read_text().splitlines()]
        assert int(rows[-1][6], 16) == 1, name + ' did not finish Pride and reach next main level'
        results[name] = hashes(log)
        assert len(results[name]) == 2
        print(name, 'ordinary route completes with original dictionary retained PASS', flush=True)
    assert results['native'] == baseline, 'Native baseline changed after original-query forwarding'
    assert results['md-aot'] == results['md-lle'], 'Terrain AOT/LLE final hashes differ'
    assert results['md256'] == results['md-aot'] and traces['md256'] == traces['md-aot'], 'Terrain source depends on presentation width'
    assert traces['md-aot'] == traces['md-lle'], 'Terrain query order or attributes differ by execution mode'
    assert (out / 'md-aot/game.ram').read_bytes() == (out / 'md-lle/game.ram').read_bytes()
    changed = sorted({cell for _, cell, a, b in traces['md-aot'] if a != b})
    (out / 'report.json').write_text(json.dumps({'result': 'PASS', 'scope': __doc__,
        'hashes': results, 'query_count': len(traces['md-aot']), 'changed_cells_observed': changed,
        'query_sites_observed': sorted({hex(pc) for pc, _, _, _ in traces['md-aot']}),
        'native_baseline_unchanged': True, 'collision_dictionary_unchanged': True,
        'cached_installed_data_used': True, 'native_256_viewport_independent': True}, indent=2) + '\n')


if __name__ == '__main__':
    main()
