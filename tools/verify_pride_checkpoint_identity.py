"""Verify static checkpoint-head identity and native OAM-referenced CHR."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from analyze_pride_scene_oam import records, slot_data
from pride_sprite_catalog import snes_frame, md_frame, bitmap


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/pride-checkpoint-art'
    out.mkdir(exist_ok=True)
    report_path = out / 'report.json'
    report_path.write_text('{"result":"RUNNING"}\n')
    native_path = ROOT / 'Lion King, The (USA).sfc'
    md_path = ROOT / 'Lion King, The (World).md'
    assert digest(native_path) == '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert digest(md_path) == 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    native = native_path.read_bytes()
    external = md_path.read_bytes()
    image = bitmap(native, snes_frame(native, 0x456de), False, with_origin=True)
    other = bitmap(external, md_frame(external, 0x973b6), True, with_origin=True)
    assert image == other
    left, top, width, height, indices = image
    assert (left, top, width, height) == (-58, -72, 33, 31)
    (out / 'shared-indexed-image.bin').write_bytes(indices)
    original = ROOT / 'build/pride-scene-oam-audit/native/native-oam.bin'
    oam_report = json.loads((ROOT / 'build/pride-scene-oam-audit/report.json').read_text())
    assert oam_report['read_only_guest_and_full_tracked_ram_exact']
    assert digest(original) == oam_report['artifacts_sha256']['raw']
    fixtures = out / 'copied-ram-cases.bin'
    count = positives = fields = compared = hero_rejections = 0
    duplicate_producer_fields = []
    ordinary_scenes = set()
    selected = None
    collection_inputs = []
    ordinary_collectible_cases = interaction_cases = 0
    with fixtures.open('wb') as f:
        def case(ram, draw, pose, fixed, expected):
            nonlocal count, positives
            f.write(struct.pack('<4I', draw, pose, fixed, expected))
            f.write(ram)
            count += 1
            positives += expected

        for record in records(original):
            ram = record['ram']
            age = record['head'][1]
            groups = {}
            for piece in record['pieces']:
                groups.setdefault(piece[3], []).append(piece)
            for draw, pieces in groups.items():
                position = struct.unpack_from('<H', ram, draw+4)[0]
                task = position-8
                descriptor = int.from_bytes(ram[task+4:task+7], 'little')
                expected = descriptor == 0xc588a6
                pose, fixed = pieces[0][9], pieces[0][7]
                if expected:
                    ordinary_scenes.add(record['head'][19])
                    assert all(p[9] == 0xc456de and not p[7] for p in pieces)
                    assert len(pieces) in (8, 16)
                    if len(pieces) == 16:
                        duplicate_producer_fields.append(age)
                    selected = ram, draw, task, pose
                elif pose == 0xc456de:
                    assert pieces[0][12], 'Unexpected non-hero owner of shared image'
                    hero_rejections += 1
                case(ram, draw, pose, fixed, expected)
                if not expected or age < 298:
                    continue
                # Actual physical OAM, not the early unpresented producer batch.
                slots = slot_data(record)
                displayed_pieces = []
                for piece in pieces:
                    x, y, attr, _, size, slot = piece[:6]
                    displayed = slots[slot]
                    if (displayed['x'], displayed['y'], displayed['attr'], displayed['size']) == (x, y&255, attr, size):
                        displayed_pieces.append(piece)
                assert len(displayed_pieces) == 8 and len({p[5] for p in displayed_pieces}) == 8, age
                for piece in displayed_pieces:
                    x, y, attr, _, size, slot = piece[:6]
                    assert ((attr>>9)&7) == 0 and not (attr & 0xc000)
                    for py in range(size):
                        state, _, _ = record['raster'][(y+py)&255]
                        vram = record['vram'][state[7]*65536:(state[7]+1)*65536]
                        base = (state[1]&7)<<13
                        if attr&256:
                            base += ((state[1]&0x18)+8)<<9
                        for px in range(size):
                            tile = ((((attr&255)>>4)+py//8)<<4) | (((attr&15)+px//8)&15)
                            address = ((base+tile*16)&32767)*2 + (py&7)*2
                            value = sum(((vram[address+(plane&1)+(16 if plane>=2 else 0)] >> (7-(px&7)))&1)<<plane for plane in range(4))
                            ix, iy = piece[10]+px-left, piece[11]+py-top
                            expected_index = indices[iy*width+ix] if 0 <= ix < width and 0 <= iy < height else 0
                            assert value == expected_index, (age, slot, px, py, value, expected_index)
                            compared += 1
                fields += 1
        assert selected and fields == 63 and hero_rejections
        collection_scene = ROOT/'build/pride-checkpoint-player/candidate1-windows-3685/256-both-aot/scene.json'
        if collection_scene.exists():
            scene = json.loads(collection_scene.read_text())
            draw = next(p['object'] for p in scene['pieces'] if p['pose'] == 0xc456de and p['position_pointer'] != 0xb21b)
            collection_inputs.append(collection_scene)
            for frame in range(3400,3741,5):
                snapshot = ROOT/f'build/pride-checkpoint-player/collection-ram/hl_wram_{frame}.bin'
                ram = snapshot.read_bytes()
                position = struct.unpack_from('<H',ram,draw+4)[0]
                if not 0xa008 <= position <= 0xff88:
                    continue
                task = position-8
                descriptor = int.from_bytes(ram[task+4:task+7],'little')
                pose = int.from_bytes(ram[draw+10:draw+13],'little')
                if descriptor != 0xc5889a or pose not in (0xc456de,0xc2fde1,0xc2fe18):
                    continue
                assert struct.unpack_from('<HH',ram,position) == (1200,112)
                case(ram,draw,pose,False,True)
                collection_inputs.append(snapshot)
                ordinary_collectible_cases += 1
                if pose != 0xc456de:
                    interaction_cases += 1
                    # Offline static-descriptor misuse and stale current-pose guards.
                    changed = bytearray(ram)
                    changed[task+4:task+7] = bytes.fromhex('a688c5')
                    case(changed,draw,pose,False,False)
                    case(ram,draw,0xc456de,False,False)
            assert ordinary_collectible_cases
            collection_inputs.append(ROOT/'build/pride-checkpoint-player/collection-probe.log')
        ram, draw, task, pose = selected
        # Unit-only structural fixtures; original captures and guests stay intact.
        for offset, value in ((draw+4, 0), (task+12, 0), (task+4, 0), (draw+10, 0),
                              (0x1ff9e, 1), (0xdf, 0), (0xe1, 0)):
            changed = bytearray(ram)
            changed[offset] = value
            assert changed != ram
            case(changed, draw, pose, False, False)
        case(ram, draw, pose, True, False)
        case(ram, draw, pose+1, False, False)
        case(ram, 0x7fff, pose, False, False)
        case(ram, 0xffe9, pose, False, False)
        for new_task, new_draw in ((0xa813, 0xdb00), (0xc013, 0xe100)):
            changed = bytearray(ram)
            changed[new_task:new_task+128] = ram[task:task+128]
            changed[new_draw:new_draw+24] = ram[draw:draw+24]
            changed[task:task+128] = bytes(128)
            changed[draw:draw+24] = bytes(24)
            struct.pack_into('<H', changed, new_draw+4, new_task+8)
            struct.pack_into('<H', changed, new_task+12, new_draw)
            case(changed, new_draw, pose, False, True)
        changed = bytearray(ram)
        struct.pack_into('<H', changed, 0xdf, 0x80d)
        case(changed, draw, pose, False, True)
    binary = out / 'checkpoint-role.exe'
    command = ['C:/mingw32/bin/gcc.exe', '-std=c11', '-Wall', '-Wextra', '-Werror',
               '-I'+str(ROOT/'engine/runner'), str(ROOT/'tools/pride_checkpoint_role_oracle.c'), '-o', str(binary)]
    with (out / 'role-build.log').open('wb') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = subprocess.run([str(binary), str(native_path), str(fixtures)], capture_output=True, check=True)
    (out / 'role.log').write_bytes(result.stdout + result.stderr)
    assert f'{count} copied-RAM cases, {positives} positive' in result.stdout.decode()
    gpu_path = ROOT / 'build/pride-gpu-clock/report.json'
    gpu = json.loads(gpu_path.read_text())
    assert gpu['result'] == 'PASS' and gpu['static_checkpoint_head_separate'] and gpu['revival_fields'] == 74
    for name, sha in gpu['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
    sources = [Path(__file__), ROOT/'tools/pride_checkpoint_role_oracle.c', ROOT/'engine/runner/tlk_checkpoint_role.h',
               ROOT/'tools/pride_sprite_catalog.py', ROOT/'tools/analyze_pride_scene_oam.py', native_path, md_path,
               original, ROOT/'build/pride-scene-oam-audit/report.json', gpu_path, *collection_inputs]
    report = dict(result='PASS', scope=__doc__, original_native_fields=fields,
        original_native_oam_texture_indices=compared, shared_bitmap_indices=len(indices),
        copied_ram_cases=count, positive_cases=positives, original_hero_rejections=hero_rejections,
        relocated_task_and_draw_fixtures=2, unit_guest_fixture_mutations_only=True,
        descriptor_table_callback_image_and_rtl_rejection_verified=True,
        duplicate_producer_fields=duplicate_producer_fields,
        ordinary_scene_ids=sorted(ordinary_scenes), alternate_080d_scene_unit_fixture_only=True,
        ordinary_collectible_c5889a_copied_ram_cases=ordinary_collectible_cases,
        ordinary_interaction_pose_copied_ram_cases=interaction_cases,
        classification_proves_visibility=False, production_adapter_enabled=False,
        final_composited_pixels_verified=False,
        full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in sources},
        artifacts_sha256={p.name: digest(p) for p in (fixtures, binary, out/'shared-indexed-image.bin', out/'role.log', out/'role-build.log')})
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print(result.stdout.decode().strip())
    print(fields, 'native OAM fields,', compared, 'OAM-referenced CHR indices, independent SNES/MD static image exact PASS')


if __name__ == '__main__':
    main()
