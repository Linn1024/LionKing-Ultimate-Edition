"""Verify the native Continue reload's nine ROM decompression recipes."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-continue-reload-assets'; out.mkdir()
    reference = ROOT/'build/pride-continue-reload-probe/capture/report.json'
    assert bound(reference)['result'] == 'OBSERVED'
    decoder = ROOT/'build/pride-final-asset-payload/report.json'
    assert bound(decoder)['result'] == 'PASS'
    library = decoder.parent/'decode.dll'
    assert digest(library) == json.loads(decoder.read_text())['artifacts_sha256']['decode.dll']
    dll = C.CDLL(str(library))
    dll.TlkMdDecompress.argtypes = [C.c_void_p,C.c_uint,C.c_uint,C.c_void_p,C.c_uint,C.c_void_p]
    rom_path = ROOT/'Lion King, The (USA).sfc'; rom = rom_path.read_bytes()
    data = C.create_string_buffer(rom); checks = {}; recipes = []
    rows = list(csv.DictReader((reference.parent/'loads.csv').open()))
    assert len(rows) == 18
    for index in range(9):
        entry, end = rows[index*2:index*2+2]; number = index+1
        assert entry['phase'] == 'entry' and end['phase'] == 'exit'
        source = int(entry['source'],16); destination = int(entry['destination'],16)
        finish = int(end['destination'],16); size = finish-destination
        buffer = C.create_string_buffer(65536); written = C.c_uint()
        checks[f'{number}/decode'] = bool(dll.TlkMdDecompress(data,len(rom),source&0x3fffff,
            buffer,len(buffer),C.byref(written)))
        checks[f'{number}/length'] = written.value == size
        offset = destination&0x1ffff
        original = (reference.parent/f'{number}-after.bin').read_bytes()
        checks[f'{number}/payload'] = buffer.raw[:size] == original[offset:offset+size]
        checks[f'{number}/port'] = int(end['port'],16) == (finish&0x1ffff)
        recipes.append(dict(source=source,destination=destination,source_end=int(end['source'],16),
            destination_end=finish,size=size,native_fields=int(end['age'])-int(entry['age'])))
    paths = [Path(__file__),reference,decoder,library,rom_path]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,recipes=recipes,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks;',sum(r['native_fields'] for r in recipes),'native decode fields',flush=True)
    assert all(checks.values())


if __name__ == '__main__': main()
