"""Execute original contact classifiers on controlled attribute fixtures.

This proves the shared wall-classification contract, not complete actor behavior
or level completion. Synthetic records are confined to isolated research cores.
Use .tools/python32/python.exe after building the native oracle DLL.
"""
import ctypes as C
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT
from pride_sprite_catalog import read_rom
from audit_pride_collision import main as audit_static_collision


def main():
    snes = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native = C.CDLL(str(ROOT / 'build/pride_terrain_native.dll'))
    native.terrain_native_init.argtypes = [C.c_void_p, C.c_uint]
    native.terrain_native_classify.argtypes = [C.c_uint, C.c_uint, C.POINTER(C.c_uint)]
    native.terrain_native_height.argtypes = [C.c_uint, C.c_uint, C.POINTER(C.c_uint)]
    native.terrain_native_floor.argtypes = [C.c_uint, C.c_uint, C.c_uint, C.POINTER(C.c_uint)]
    assert native.terrain_native_init(snes, len(snes))
    game = MdLab()
    state = C.create_string_buffer((ROOT / 'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
    game.core.retro_unserialize.restype = C.c_bool
    assert game.core.retro_unserialize(state, len(state)-1)
    def word(a, value):
        game.work_ram[a] = value & 255
        game.work_ram[a+1] = (value >> 8) & 255
    def pointer(a, value):
        word(a, value >> 16); word(a+2, value)
    # JSR original 00267E; MOVE SR,D2; park in a local BRA loop.
    # D1 is the unmodified attribute return. No original instructions patched.
    game.write_code(0xfe00, bytes.fromhex('4eb90000267e40c260fe'))
    pointer(0xcd2e, 0xffe100); pointer(0xcd46, 0xff93ce)
    word(0xe000, 0)
    rows = []
    heights = []
    floors = []
    try:
        for flags in (0, 8):
            game.work_ram[(0x93ce+0x43)^1] = flags
            for attribute in range(256):
                game.work_ram[0xe102^1] = attribute
                game.core.m68k_set_reg(12, 0xffe000)
                game.core.m68k_set_reg(17, 0x2700)
                game.core.m68k_set_reg(15, 0xfffd00)
                game.core.m68k_set_reg(16, 0xfffe00)
                game.step()
                result = (C.c_uint * 3)()
                assert native.terrain_native_classify(attribute, flags, result)
                actual = [game.core.m68k_get_reg(1) & 65535, game.core.m68k_get_reg(2) & 1]
                assert actual == list(result[:2]), (attribute, flags, actual, list(result))
                rows.append({'attribute': attribute, 'actor_flags': flags,
                             'returned_attribute': actual[0], 'blocking': bool(actual[1])})
        # Original point-height query 002B8E takes X/Y word arguments on stack.
        # A varying 16-byte row checks indexing as well as every possible byte.
        pointer(0xcd22, 0xffe000); pointer(0xcd32, 0xffe200)
        word(0xcd1e, 2); word(0xe100, 0)
        for base in range(256):
            for x in range(16):
                game.work_ram[(0xe200+x)^1] = (base+x) & 255
            for x in range(16):
                code = bytes.fromhex('3f3c00003f3c') + x.to_bytes(2, 'big') + bytes.fromhex('4eb900002b8e588f60fe')
                game.write_code(0xfe00, code)
                game.core.m68k_set_reg(17, 0x2700)
                game.core.m68k_set_reg(15, 0xfffd00)
                game.core.m68k_set_reg(16, 0xfffe00)
                game.step()
                result = (C.c_uint * 2)()
                assert native.terrain_native_height(base, x, result), (base, x, 'SNES return')
                actual = game.core.m68k_get_reg(0) & 65535
                assert actual == result[0] == ((base+x) & 31), (base, x, actual, list(result))
                heights.append({'base': base, 'column': x, 'height': actual})
        pointer(0xcd22, 0xffc000); word(0xcd1e, 200)
        word(0xccc6, 1056); word(0xccfe, 0)
        word(0xc000, 0); word(0xc0c8, 8); word(0xc190, 0); word(0xc258, 0)
        word(0xe100, 0); word(0xe104, 0x0100)
        game.work_ram[0xe102^1] = 0x11; game.work_ram[0xe106^1] = 0xff
        game.write_code(0xfe00, bytes.fromhex('4eb9000022c040c360fe'))
        for base in range(256):
            for x in range(32):
                game.work_ram[(0xe200+x)^1] = (base+x) & 255
            for x in (0, 3, 7, 8, 15):
                for y in (12, 15, 16, 23, 24, 31, 32, 47):
                    game.core.m68k_set_reg(0, x); game.core.m68k_set_reg(1, y)
                    game.core.m68k_set_reg(17, 0x2700)
                    game.core.m68k_set_reg(15, 0xfffd00); game.core.m68k_set_reg(16, 0xfffe00)
                    game.step()
                    result = (C.c_uint * 4)()
                    assert native.terrain_native_floor(base, x, y, result), (base, x, y, 'SNES floor return')
                    actual = [game.core.m68k_get_reg(3) & 1, game.core.m68k_get_reg(0) & 65535,
                              game.core.m68k_get_reg(1) & 255, game.core.m68k_get_reg(2) & 255]
                    assert actual[0] == result[0] and actual[2:] == list(result[2:]), (base, x, y, actual, list(result))
                    if actual[0]:
                        assert actual[1] == result[1], (base, x, y, 'floor delta', actual, list(result))
                    floors.append({'base': base, 'column': x, 'y': y, 'contact': bool(actual[0]),
                                   'delta': actual[1] if actual[0] else None,
                                   'attribute': actual[2], 'above_attribute': actual[3]})
    finally:
        game.close()
    out = ROOT / 'build/pride-terrain'
    out.mkdir(parents=True, exist_ok=True)
    audit_static_collision()
    collision = json.loads((ROOT / 'build/pride-collision-audit.json').read_text())
    classification = {(r['attribute'], r['actor_flags']): r['blocking'] for r in rows}
    assert classification[2, 0] and not classification[2, 8], 'Actor flag branch was not exercised'
    assert all(classification[255, f] and not classification[17, f] for f in (0, 8))
    assert {r['contact'] for r in floors} == {False, True}
    assert {r['above_attribute'] for r in floors} == {0, 17, 255}, 'Second-row paths were not exercised'
    contacts = []
    for cell in collision['metadata_or_profile_differences']:
        a, b = bytes.fromhex(cell['snes_flags'])[0], bytes.fromhex(cell['md_flags'])[0]
        if a == b:
            continue
        contacts.append({**cell, 'classifications': [
            {'actor_flags': flags, 'snes_blocking': classification[a, flags],
             'md_blocking': classification[b, flags]} for flags in (0, 8)]})
    changed = [c for c in contacts if any(r['snes_blocking'] != r['md_blocking'] for r in c['classifications'])]
    assert len(contacts) == 21 and len(changed) == 11
    cleared = sum(c['snes_flags'] == 'ff00' and c['md_flags'] == '0000' for c in changed)
    added = sum(c['snes_flags'] == '1100' and c['md_flags'] == 'fa00' for c in changed)
    assert cleared == 7 and added == 4
    (out / 'contact-cells.json').write_text(json.dumps({'result': 'PASS',
        'scope': 'Static cell attributes passed through executed original wall classifiers; actor reactions remain separate',
        'different_contact_cells': contacts, 'changed_wall_classification_cells': len(changed),
        'cleared_wall_cells': cleared, 'added_wall_cells': added,
        'point_height_upper_bits_ignored': True,
        'native_record_alias_conflicts': collision['contact_record_alias_conflicts'],
        'different_full_height_cells': collision['total_cells'] - collision['matching_full_height_cells']}, indent=2) + '\n')
    (out / 'classifier.json').write_text(json.dumps({'result': 'PASS', 'scope': __doc__,
        'snes_entry': 'C0C7C2', 'md_entry': '00267E', 'cases': rows,
        'point_height_entries': ['C079D2', '002B8E'], 'point_height_cases': heights,
        'floor_entries': ['C0C4A7', '0022C0'], 'floor_cases': floors}, indent=2) + '\n')
    print('Original SNES/MD contact classifiers:', len(rows), 'fixtures agree PASS', flush=True)
    print('Original point heights:', len(heights), 'byte/index fixtures agree PASS', flush=True)
    print('Original floor probes:', len(floors), 'contact/delta/attribute fixtures agree PASS', flush=True)
    print('Pride map: 21 contact differences; 7 cleared and 4 added wall cells; 512 upper-bit variants ignored by point-height query PASS', flush=True)


if __name__ == '__main__':
    main()
