"""Audit second-level camera-wrap and checkpoint-palette inputs in both originals.

Native samples come from ordinary power-on controller replay in compiled and
interpreted hosts. MD samples are the retained unforced original reference.
This records source contracts and reachability, not complete mixed rendering.
No ROM, actor, camera, checkpoint or RNG values are written.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path

from audit_scenes import ROOT, read_rom
from verify_windows import hashes


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word(data, address):
    return struct.unpack_from('<H', data, address)[0]


def summarize(rows):
    assert rows, 'No second-level samples'
    offsets = sorted({r['offset'] for r in rows})
    assert all(v % 512 == 0 for v in offsets), 'Unexpected camera-wrap unit'
    changes = []
    for previous, current in zip(rows, rows[1:]):
        if previous['offset'] != current['offset']:
            changes.append({'before': previous, 'after': current})
    assert changes and max(offsets) >= 1024, 'Ostrich ride not exercised'
    return {'samples': len(rows), 'frame_range': [rows[0]['frame'], rows[-1]['frame']],
            'offset_range': [min(offsets), max(offsets)], 'observed_offsets': offsets,
            'palette_variant_counts': {str(v): sum(r['palette_variant'] == v for r in rows) for v in (0, 1)},
            'wrap_changes': changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse', action='store_true', help='Recheck retained native outputs')
    args = parser.parse_args()
    out = ROOT/'build/cant-wait-native'
    out.mkdir(parents=True, exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING', 'scope': __doc__})+'\n')
    snes = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    head = ROOT/'engine/build-win/tlk_headless.exe'
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    profile = out/'native.ini'
    profile.write_text('schema = 1\ngame = snes\n')
    frames = list(range(5000, 13501, 16))
    results = {}
    sampled = {}
    for mode in ('aot', 'lle'):
        folder = out/mode
        folder.mkdir(exist_ok=True)
        log = folder/'run.log'
        if not args.reuse:
            env = os.environ.copy()
            env.update(TLK_WRAM_DUMP=','.join(map(str, frames)), TLK_WRAM_DIR=str(folder))
            cmd = [head, '--rom', ROOT/'Lion King, The (USA).sfc', '--resource-profile', profile,
                   '--input-polled', tape, '--frames', 13500, '--ram-log', folder/'route.ram']
            if mode == 'lle':
                cmd.append('--lle')
            with log.open('wb') as output:
                subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, stdout=output,
                               stderr=subprocess.STDOUT, check=True, timeout=300)
        rows = []
        sample_hash = hashlib.sha256()
        for frame in frames:
            data = (folder/f'hl_wram_{frame}.bin').read_bytes()
            assert len(data) == 131072
            sample_hash.update(data)
            if word(data, 0x1ff9e) != 1 or word(data, 0xdf) != 0x3b9:
                continue
            # Original C072F7 selects C601B7 for DMA only after a checkpoint
            # with a saved X different from descriptor+16; C50B7C otherwise.
            variant = int(bool(word(data, 0x1ffa2)) and word(data, 0x1ffa4) != word(snes, 0x3b9+0x16))
            rows.append({'frame': frame, 'camera_x': word(data, 0xb29b),
                         'offset': word(data, 0xa58), 'ride_active': bool(word(data, 0xa56)),
                         'palette_transition_started': bool(word(data, 0xa4a)),
                         'native_palette_target': word(data, 0xc3) | data[0xc5] << 16,
                         # C09E30 loads this into CGADD ($2121); it is not a
                         # fade timer. C6 is the byte count, CA the DMA request.
                         'native_palette_cgram_start': word(data, 0xc8),
                         'native_palette_dma_bytes': word(data, 0xc6),
                         'native_palette_dma_pending': bool(word(data, 0xca)),
                         'checkpoint_present': bool(word(data, 0x1ffa2)),
                         'checkpoint_x': word(data, 0x1ffa4), 'palette_variant': variant})
        sampled[mode] = rows
        results[mode] = {'hashes': hashes(log), 'wram_samples_sha256': sample_hash.hexdigest(),
                         'tracked_ram_sha256': digest(folder/'route.ram'), **summarize(rows)}
        print(mode, len(rows), 'native second-level samples checked', flush=True)
    assert results['aot'] == results['lle'], 'Native execution modes differ'
    assert len(results['aot']['hashes']) == 2
    source = ROOT/'build/md-next-levels-replay/scene-backgrounds.json'
    original = [r for r in json.loads(source.read_text()) if r['level'] == 1 and r['display_enabled']
                and r['normal_background_palette_variants']]
    md_rows = [{'frame': r['frame'], 'camera_x': r['camera_x'], 'offset': r['offset_x'],
                'palette_variant': int(bool(r['checkpoint_position']))} for r in original]
    # Initializer selection is not the palette lifecycle: the original also
    # creates palette-transition objects at 18D6B6/18D6E0. Preserve contrary
    # live evidence instead of assigning the checkpoint test to every field.
    disagreements = [r for r in original if r['normal_background_palette_variants'] != [int(bool(r['checkpoint_position']))]]
    observed_md_rows = [{**row, 'palette_variant': source_row['normal_background_palette_variants'][0]}
                        for row, source_row in zip(md_rows, original)]
    descriptor_palette = int.from_bytes(md[0x1cfdb4+48+44:0x1cfdb4+48+48], 'big')
    assert descriptor_palette == 0xffff845c, 'Dynamic palette descriptor changed'
    sources = {'native': [0xc50b7c, 0xc601b7], 'md': [0x1ea604, 0x1ea684]}
    contracts = {}
    # Hash entire bounded original routines, keeping cartridge bytes out of
    # tracked source. Disassemblies and captures remain local research data.
    for name, rom, start, end in [('native_wrap', snes, 0xb35f, 0xb3c3),
                                  ('native_palette_loader', snes, 0x72f7, 0x7353),
                                  ('native_palette_trigger', snes, 0xd178, 0xd1cf),
                                  ('native_palette_dma', snes, 0x9e26, 0x9e5a),
                                  ('md_wrap', md, 0x8b9ba, 0x8ba28),
                                  ('md_palette_loader', md, 0x8bec8, 0x8bf34)]:
        contracts[name] = {'rom_offset_range': [start, end], 'sha256': hashlib.sha256(rom[start:end]).hexdigest()}
    palettes = {}
    for console, addresses in sources.items():
        rom = snes if console == 'native' else md
        size = 510 if console == 'native' else 128
        palettes[console] = [{'source': hex(a), 'bytes': size,
                             'sha256': hashlib.sha256(rom[a & 0x3fffff:(a & 0x3fffff)+size]).hexdigest()}
                            for a in addresses]
    report = {'result': 'WRAP_INPUTS_VERIFIED_PALETTE_LIFECYCLE_OPEN', 'scope': __doc__, 'headless_sha256': digest(head),
              'audit_source_sha256': digest(ROOT/'tools/audit_cant_wait_native.py'),
              'tape_sha256': digest(tape), 'md_reference_sha256': digest(source),
              'native': results, 'md_checkpoint_inputs': summarize(md_rows),
              'md_observed_palette': summarize(observed_md_rows),
              'md_checkpoint_only_palette_disagreements': len(disagreements),
              'md_checkpoint_only_palette_first_disagreement': disagreements[0]['frame'] if disagreements else None,
              'original_routine_contracts': contracts,
              'palette_sources': palettes, 'md_descriptor_palette_is_ram': hex(descriptor_palette),
              'native_offset_address': '7E0A58', 'md_offset_address': 'FFCD00',
              'wrap_unit_pixels': 512, 'native_default_checkpoint_x': word(snes, 0x3b9+0x16),
              'native_palette_choice_scope': 'Original initializer branch only; live palette transition is separate',
              'native_transition_contract': {
                  'trigger': 'C0D178: first eligible object position sets A4A and requests alternate palette',
                  'target': 'C601B5', 'cgram_start': 'C8 -> CGADD at C09E30',
                  'byte_count': 'C6 -> DMA5 count at C09E4C',
                  'pending': 'CA gates DMA at C09E26 and clears at C09E57',
                  'scope': 'This path requests a direct DMA; C8 is not an MD-style palette fade clock'},
              'background_enabled': False,
              'remaining': ['Map original palette-transition objects; checkpoint alone is insufficient',
                            'Native displayed DMA ownership and MD fade-clock correspondence',
                            'Mixed renderer with latched camera-plus-wrap inputs and palette ownership',
                            'Mixed pixel checks, transitions, live source switches and moving saves']}
    (out/'native-samples.json').write_text(json.dumps(sampled, indent=2)+'\n')
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Second-level wrap inputs verified;', len(disagreements), 'live palette fields require transition mapping; adapter remains guarded', flush=True)


if __name__ == '__main__':
    main()
