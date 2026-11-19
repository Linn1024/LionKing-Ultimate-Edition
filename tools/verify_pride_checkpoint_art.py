"""Verify detached checkpoint-head frame/palette combinations against both ROMs."""
import hashlib
import csv
import json
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from analyze_pride_scene_oam import records
from pride_sprite_catalog import bitmap, snes_frame, md_frame


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/pride-checkpoint-art'
    identity_path = out / 'report.json'
    identity = json.loads(identity_path.read_text())
    assert identity['result'] == 'PASS' and identity['original_native_oam_texture_indices'] == 68544
    for name, sha in identity['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
    for name, sha in identity['artifacts_sha256'].items():
        assert digest(out/name) == sha, name
    snes_path, md_path = ROOT/'Lion King, The (USA).sfc', ROOT/'Lion King, The (World).md'
    snes, md = snes_path.read_bytes(), md_path.read_bytes()
    includes = ['-I'+str(ROOT/'engine/runner'), '-I'+str(ROOT/'engine/snesrecomp/runner/src')]
    own_sources = [ROOT/'tools/pride_checkpoint_art_oracle.c', ROOT/'engine/runner/tlk_checkpoint_art.c']
    dependencies = [ROOT/'engine/runner/tlk_revival_art.c', ROOT/'engine/runner/tlk_death_scene.c',
                    ROOT/'engine/snesrecomp/runner/src/sha256.c']
    binary = out / 'checkpoint-art.exe'
    with (out/'art-build.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/gcc.exe', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-fsyntax-only', *includes, *map(str, own_sources)], stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run(['C:/mingw32/bin/gcc.exe', '-std=c11', '-O2', *includes,
                        *map(str, own_sources+dependencies), '-o', str(binary)], stdout=log, stderr=subprocess.STDOUT, check=True)
    data_path = out / 'owned-art.bin'
    run = subprocess.run([str(binary), str(snes_path), str(md_path), str(data_path)], capture_output=True, check=True)
    (out/'art.log').write_bytes(run.stdout+run.stderr)
    data = data_path.read_bytes()
    assert data[:8] == b'CHKART01'
    bounds = struct.unpack_from('<4i', data, 8)
    assert bounds == (-58, -72, 33, 31)
    n = bounds[2]*bounds[3]
    base_end = 24+n*2+n*4*2
    assert len(data) > base_end
    images = [bitmap(snes, snes_frame(snes, 0x456de), False, with_origin=True),
              bitmap(md, md_frame(md, 0x973b6), True, with_origin=True)]
    palettes = [struct.unpack_from('<16H', snes, 0x7b93), []]
    source_md = struct.unpack_from('>16H', md, 0x1d78aa)
    for raw in source_md:
        palettes[1].append(sum((((raw>>s)&7)*4+(((raw>>s)&7)>>2))<<o for s, o in ((1, 0), (5, 5), (9, 10))))
    native_fields = 0
    native_path = ROOT/'build/pride-scene-oam-audit/native/native-oam.bin'
    for record in records(native_path):
        if record['head'][1] < 298:
            continue
        assert all(struct.unpack('<256H', line[2])[129:144] == palettes[0][1:] for line in record['raster'])
        native_fields += 1
    assert native_fields == 63
    palette_path = ROOT/'build/pride-death-controller/original-palettes.csv'
    target = [sum(((v>>s)&7)<<o for s, o in ((1, 0), (5, 3), (9, 6))) for v in source_md]
    palette_rows = [r for r in csv.DictReader(palette_path.open())
                    if r['case'] == '0' and int(r['age']) >= 270 and int(r['index']) < 16]
    assert len(palette_rows) == 1216
    assert all(target[int(r['index'])] == int(r['next_color']) for r in palette_rows)
    sat_path = ROOT/'build/pride-scene-sat-full/fields.json'
    sat = {row['age']: row for row in json.loads(sat_path.read_text())}
    visible_path = ROOT/'build/pride-gpu-clock/visible-poses.json'
    visible = [row for row in json.loads(visible_path.read_text()) if row['phase'] == 'revival']
    assert len(visible) == 74
    for row in visible:
        first = 9+len(md_frame(md, row['md_pose']))
        assert all(piece['palette'] == 0 for piece in sat[row['age']]['sprites'][first:first+3])
    for source, image in enumerate(images):
        assert image[:4] == bounds
        assert data[24+source*n:24+(source+1)*n] == image[4]
    colors = struct.unpack_from('<'+str(n*4)+'H', data, 24+n*2)
    opaque = 0
    for frames in range(2):
        for palette in range(2):
            expected = [palettes[palette][index] if index else 0xffff for index in images[frames][4]]
            at = (frames*2+palette)*n
            assert list(colors[at:at+n]) == expected, (frames, palette)
            opaque += sum(index != 0 for index in images[frames][4])
    assert 'flash/identity/atomic guards PASS' in run.stdout.decode()
    extra_indices = extra_colors = extra_opaque = 0
    offset = base_end
    for native,external in ((0x2fde1,0x977c6),(0x2fe18,0x977fe)):
        pose,*shape = struct.unpack_from('<I4i',data,offset)
        offset += 20
        assert pose == native|0xc00000 and shape == [-58,-72,32,30]
        pairs = [bitmap(snes,snes_frame(snes,native),False,with_origin=True),
                 bitmap(md,md_frame(md,external),True,with_origin=True)]
        size = shape[2]*shape[3]
        for image in pairs:
            assert list(image[:4]) == shape
            assert data[offset:offset+size] == image[4]
            offset += size
            extra_indices += size
        for frames in range(2):
            for palette in range(2):
                actual = struct.unpack_from('<'+str(size)+'H',data,offset)
                expected = tuple(palettes[palette][index] if index else 0xffff for index in pairs[frames][4])
                assert actual == expected,(hex(pose),frames,palette)
                offset += size*2
                extra_colors += size
                extra_opaque += sum(index != 0 for index in pairs[frames][4])
    assert offset == len(data)
    sources = [Path(__file__), *own_sources, *dependencies, ROOT/'engine/runner/tlk_checkpoint_art.h',
               ROOT/'engine/runner/tlk_checkpoint_role.h', ROOT/'engine/runner/tlk_revival_art.h',
               ROOT/'engine/runner/tlk_death_scene.h', identity_path, snes_path, md_path,
               native_path, palette_path, sat_path, visible_path, ROOT/'tools/analyze_pride_scene_oam.py']
    report = dict(result='PASS', scope=__doc__, source_indexed_pixels=n*2,
        independent_frame_palette_combinations=4, sampled_colors=n*4, opaque_sampled_colors=opaque,
        source_detached=True, full_rom_identity_checked=True, flash_and_atomic_rejection_verified=True,
        checkpoint_image_count=3, interaction_source_indexed_pixels=extra_indices,
        interaction_sampled_colors=extra_colors, interaction_opaque_sampled_colors=extra_opaque,
        original_native_full_palette_fields=native_fields, original_md_target_palette_entries=1216,
        original_md_static_head_palette_bank_fields=74,
        original_identity_evidence_bound=True, palette_bank0_only=True,
        guest_execution=False, renderer_integration=False, actual_windows_captured=False,
        production_adapter_enabled=False, full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in sources},
        artifacts_sha256={p.name: digest(p) for p in (binary, data_path, out/'art.log', out/'art-build.log')})
    (out/'art-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(run.stdout.decode().strip())
    print('Four independent original frame/palette combinations exact; detached component only PASS')


if __name__ == '__main__':
    main()
