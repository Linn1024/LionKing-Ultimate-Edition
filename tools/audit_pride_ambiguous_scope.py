"""Audit the five global ambiguous body entries without silently choosing bounds.

Original CPU fixtures prove age selection at literal player-action call sites.
Global artwork identity and direct-call scans do not prove all indirect or NPC
reachability. Production mappings and capability reporting remain unchanged.
Run with embedded 32-bit Python after building pride_animation_scope.dll.
"""
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom
from pride_sprite_catalog import bitmap, md_frame, snes_frame


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/pride-ambiguous-scope'
    out.mkdir(exist_ok=True)
    report_path = out/'report.json'
    report_path.write_text(json.dumps({'result': 'RUNNING', 'scope': __doc__})+'\n')
    snes = read_rom('Lion King, The (USA).sfc', '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md = read_rom('Lion King, The (World).md', 'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    library_path = ROOT/'build/pride_animation_scope.dll'
    native = C.CDLL(str(library_path))
    native.terrain_native_init.argtypes = [C.c_void_p, C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(snes), len(snes))
    native.animation_scope_branch.argtypes = [C.c_uint]*4+[C.POINTER(C.c_uint)]
    result = (C.c_uint*4)()
    guards = []
    # All ten literal calls to C37F6E (adult pounce) and four to C3836B
    # (adult grab) have these original age branches before their arguments.
    sites = [0xc31a3b, 0xc31dcf, 0xc328e3, 0xc3290f, 0xc33072, 0xc3309e,
             0xc33504, 0xc33530, 0xc3398f, 0xc339bb,
             0xc303c9, 0xc3086c, 0xc3131e, 0xc315c1]
    for entry in sites:
        at = entry & 0x3fffff
        assert snes[at:at+6] == bytes.fromhex('ad0020d0034c')
        adult = entry+8
        child = (entry & 0xff0000) | struct.unpack_from('<H', snes, at+6)[0]
        counts = {'child': 0, 'adult': 0}
        for age in range(65536):
            assert native.animation_scope_branch(entry, age, child, adult, result)
            assert result[0] == (adult if age else child), (hex(entry), age, list(result))
            counts['adult' if age else 'child'] += 1
        guards.append({'entry': hex(entry), 'child_skip': hex(child), 'adult_path': hex(adult),
                       'cases': 65536, 'outcomes': counts})
    # Original PEA/JSL sequences feed C196D2; execute them, retaining their
    # real stack arguments and cleanup, instead of reproducing a selector.
    selectors = []
    for entry, stop, child, adult in [(0xc326e3, 0xc32701, 0xc0ea9c, 0xc0e366),
                                      (0xc3275d, 0xc3277b, 0xc0dfe8, 0xc0e028)]:
        for age in range(65536):
            assert native.animation_scope_branch(entry, age, stop, stop, result)
            assert result[1] == (adult if age else child) and result[2] == 0x1ff0
        selectors.append({'entry': hex(entry), 'child_callback': hex(child),
                          'adult_callback': hex(adult), 'cases': 65536, 'stack_restored': True})
    portrait = []
    for age in range(65536):
        assert native.animation_scope_branch(0xc087c5, age, 0xc087ca, 0xc087df, result)
        assert result[0] == (0xc087ca if age else 0xc087df)
    portrait.append({'entry': '0xc087c5', 'child': '0xc087df', 'adult': '0xc087ca', 'cases': 65536})
    source = ROOT/'build/pride-hitbox-catalog/report.json'
    ambiguous = json.loads(source.read_text())['native_fallback_ambiguous_poses']
    rows = []
    for row in ambiguous:
        p = row['snes']
        image = bitmap(snes, snes_frame(snes, p), False, with_origin=True)
        candidates = []
        for q in row['md_candidates']:
            other = bitmap(md, md_frame(md, q), True, with_origin=True)
            assert image[2:] == other[2:], 'Global cropped image match changed'
            candidates.append({'md': hex(q), 'origin': list(other[:2]),
                               'same_anchored_image': image == other,
                               'bounds': list(struct.unpack_from('>4h', md, q+12))})
        rows.append({'snes': hex(p), 'origin': list(image[:2]), 'candidates': candidates})
    literal_calls = {}
    for target in (0xc37f6e, 0xc3836b):
        needle = b'\x22'+target.to_bytes(3, 'little')
        calls = []; position = 0
        while (position := snes.find(needle, position)) >= 0:
            calls.append(0xc00000+position);position += 1
        literal_calls[hex(target)] = [hex(v) for v in calls]
    assert len(literal_calls['0xc37f6e']) == 10 and len(literal_calls['0xc3836b']) == 4
    streams = []
    for entry, pose in [(0xc0df31, 0xc01998), (0xc0ee3a, 0xc3c5d0),
                        (0xc0ef8a, 0xc3c5d0), (0xc0f3ae, 0xc3d50b),
                        (0xc0f911, 0xc6129e), (0xc0f915, 0xc612f5),
                        (0xc0f986, 0xc6129e), (0xc0f9ae, 0xc612f5)]:
        at = entry & 0x3fffff
        assert snes[at] < 128 and int.from_bytes(snes[at+1:at+4], 'little') == pose
        streams.append({'entry': hex(entry), 'pose': hex(pose), 'duration': snes[at]})
    setters = []
    for entry, stream in [(0xc0df11, 0xc0df31), (0xc0e366, 0xc0ee3a),
                          (0xc0e028, 0xc0ef8a), (0xc0e2e8, 0xc0e308),
                          (0xc0f8f1, 0xc0f911), (0xc0f98e, 0xc0f9ae)]:
        at = entry & 0x3fffff
        assert snes[at] == 0xa9 and struct.unpack_from('<H', snes, at+1)[0] == (stream & 65535)
        setters.append({'callback': hex(entry), 'stream': hex(stream)})
    npc_setters = []
    needle = b'\xa9\x66\xe3'
    for at in range(0x1a8c8, 0x1aa3e):
        if snes[at:at+3] == needle:
            npc_setters.append(hex(0xc00000+at))
    assert npc_setters == ['0xc1a92e', '0xc1a9b7'], 'Retain the other callback callers in scope'
    # Each age branch skips its actual direct call; no reliance on a nearby
    # unrelated age test to classify the call's source.
    for guard in guards:
        entry = int(guard['entry'], 16);child = int(guard['child_skip'], 16)
        calls = [int(v, 16) for values in literal_calls.values() for v in values
                 if entry < int(v, 16) < child]
        assert len(calls) == 1, ('Guard does not own exactly one action call', guard, calls)
    report = {'result': 'GUARDED_PATHS_VERIFIED_GLOBAL_SCOPE_OPEN', 'scope': __doc__,
              'original_cpu_cases': 17*65536, 'age_guards': guards, 'selectors': selectors,
              'age_selected_loader': portrait, 'literal_action_calls': literal_calls,
              'verified_original_stream_entries': streams, 'verified_callback_setters': setters,
              'unclosed_other_callback_setters': npc_setters,
              'ambiguous_anchored_images': rows, 'production_mappings_unchanged': True,
              'global_or_indirect_unreachability_proven': False,
              'remaining': ['Other NPC/indirect callers of global artwork and animation callbacks',
                            'Full Pride art/attack/enemy/difficulty and interruption checklist'],
              'source_sha256': {'snes_rom': hashlib.sha256(snes).hexdigest(),
                                 'md_rom': hashlib.sha256(md).hexdigest(),
                                 'catalog': digest(source), 'oracle_dll': digest(library_path),
                                 'oracle_source': digest(ROOT/'tools/pride_animation_scope_oracle.c'),
                                 'oracle_bus_source': digest(ROOT/'tools/pride_terrain_native_oracle.c'),
                                 'interpreter_source': digest(ROOT/'engine/build-win/tlk-runtime/interp816.c')}}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print('Original age branches/selectors:', report['original_cpu_cases'], 'cases PASS; global/NPC scope remains open', flush=True)


if __name__ == '__main__':
    main()
