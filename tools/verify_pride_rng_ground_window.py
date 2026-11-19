"""Verify the earlier live floor call against untouched original instructions."""
import csv
import ctypes as C
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data


def main():
    base = ROOT/'build/pride-rng-player2'
    capture = base/'ground-window'
    report_path = capture/'report.json'
    recorded = bound(report_path)
    build_path = base/'build-report.json'
    build = bound(build_path)
    for name, sha in build['link_inputs_sha256'].items():
        assert digest(ROOT/name) == sha, name
    assert digest(base/'player.exe') == build['binary_sha256']
    oracle_base = ROOT/'build/pride-default-grounding'
    oracle_report = json.loads((oracle_base/'build-report.json').read_text())
    library_path = oracle_base/'original-grounding.dll'
    assert digest(library_path) == oracle_report['oracle_sha256']
    sources = [Path(__file__), report_path, build_path, library_path,
               oracle_base/'build-report.json']
    for name, sha in oracle_report['source_sha256'].items():
        if name.endswith(('pride_default_grounding_oracle.c',
                          'pride_terrain_native_oracle.c', 'interp816.c',
                          'interp816.h', 'saveload.h')):
            assert digest(ROOT/name) == sha, name
            sources.append(ROOT/name)
    dll_search = __import__('os').add_dll_directory('C:/mingw32/bin')
    library = C.CDLL(str(library_path))
    library.terrain_native_init.argtypes = [C.c_void_p, C.c_uint]
    rom = (ROOT/'Lion King, The (USA).sfc').read_bytes()
    assert __import__('hashlib').sha256(rom).hexdigest() == '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert library.terrain_native_init(rom, len(rom))
    library.grounding_snapshot_run.argtypes = [C.c_void_p, C.c_uint,
        C.POINTER(C.c_uint), C.c_void_p, C.POINTER(C.c_uint), C.c_void_p, C.c_void_p]
    abi_keys = ('a', 'x', 'y', 'stack', 'direct_page', 'db', 'p', 'emulation')
    checks = {}
    observations = {}
    for mode in ('aot', 'lle'):
        folder = capture/mode
        assert recorded['runs'][mode] == dict(exit=0, last_field=4700)
        entry = next(csv.DictReader((folder/'ground-entry.csv').open()))
        returned = next(csv.DictReader((folder/'ground-return.csv').open()))
        before = (folder/'ground-entry.bin').read_bytes()
        after = (folder/'ground-return.bin').read_bytes()
        output = C.create_string_buffer(0x20000)
        reads = C.create_string_buffer(0x20000)
        writes = C.create_string_buffer(0x20000)
        result = (C.c_uint*11)()
        assert library.grounding_snapshot_run(before, len(before),
            (C.c_uint*8)(*(int(entry[k]) for k in abi_keys)), output, result, reads, writes)
        checks[mode+'/original_full_wram'] = output.raw == after
        checks[mode+'/original_return_cpu'] = list(result)[:8] == [int(returned[k]) for k in abi_keys]
        checks[mode+'/earlier_preparation'] = int(entry['age']) == int(returned['age']) == 264
        fields = list(csv.DictReader((folder/'owner-fields.csv').open()))
        health = next(row for row in fields if int(row['native_health']) > 0)
        ready = next(row for row in fields if int(row['events']) & 8)
        checks[mode+'/health_deadline'] = int(health['age']) == 274
        checks[mode+'/ready_deadline'] = int(ready['age']) == 300
        checks[mode+'/grounded_before_health'] = all(int(row['y']) == 1255 for row in fields if 264 <= int(row['age']) <= 300)
        observations[mode] = dict(instructions=result[8], invalid_bus_accesses=result[9],
            ground_age=int(entry['age']), health_age=int(health['age']), ready_age=int(ready['age']),
            changed_offsets=[i for i,(a,b) in enumerate(zip(before,after)) if a != b])
    a, b = capture/'aot', capture/'lle'
    pattern = r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows = lambda folder: re.findall(pattern, (folder/'run.log').read_text())
    checks['every_field_aot_lle'] = len(rows(a)) == 4700 and rows(a) == rows(b)
    checks['whole_pcm_aot_lle'] = wav_data(a/'audio.wav') == wav_data(b/'audio.wav')
    for name in ('ground-entry.bin', 'ground-return.bin', 'owner-fields.csv', 'owner-events.csv'):
        checks['aot_lle/'+name] = digest(a/name) == digest(b/name)
    output_path = base/'ground-window-audit.json'
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
        observations=observations, compared_fields=4700,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        full_mixture_completion_verified=False, public_player_enabled=False,
        full_first_level_fidelity_complete=False)
    output_path.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'], [k for k,v in checks.items() if not v], flush=True)
    assert all(checks.values())
    dll_search.close()


if __name__ == '__main__':
    main()
