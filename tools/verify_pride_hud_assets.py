"""Compare prepared HUD playback against the preceding independent ROM-backed module."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-hud-assets'
    build_path = base/'build-report.json'; build = bound(build_path)
    player_path = ROOT/'build/pride-hud-assets42/build-report.json'; player = bound(player_path)
    out = base/'verification'; out.mkdir()
    sha = ROOT/'engine/snesrecomp/runner/src/sha256.c'
    include = ROOT/'engine/snesrecomp/runner/src'
    original = ROOT/'engine/runner/tlk_md_hud.c'
    patched = ROOT/'build/pride-hud-assets42/game/tlk_md_hud.c'
    reader = ROOT/'engine/runner/tlk_md_hud_assets.c'
    commands = {}
    for label, sources in [('original', [original]), ('prepared', [patched, reader, sha])]:
        cmd = ['C:/mingw32/bin/gcc.exe', '-O2', '-shared', '-static-libgcc', '-I'+str(include),
               '-I'+str(ROOT/'engine/runner'), *map(str, sources), '-o', str(out/(label+'.dll'))]
        subprocess.run(cmd, check=True, cwd=ROOT)
        commands[label] = cmd
    old = C.CDLL(str(out/'original.dll')); new = C.CDLL(str(out/'prepared.dll'))
    for module in (old, new):
        module.TlkMdHudInit.argtypes = [C.c_void_p, C.c_size_t]
        module.TlkMdHudGenerate.argtypes = [C.c_uint, C.c_int, C.c_int, C.c_void_p, C.c_size_t]
        module.TlkMdHudPrepare.argtypes = [C.c_int, C.c_int, C.c_int, C.c_int, C.c_uint]
        module.TlkMdHudPixel.argtypes = [C.c_uint, C.c_int, C.c_int]
    new.TlkMdHudAssetsLoad.argtypes = [C.c_void_p, C.c_size_t]
    new.TlkMdHudAssetsReadFile.argtypes = [C.c_char_p]
    checks = {}
    rom_path = ROOT/'Lion King, The (World).md'
    rom = rom_path.read_bytes(); buffer = C.create_string_buffer(rom)
    assert old.TlkMdHudInit(buffer, len(rom))
    C.memset(buffer, 0, len(rom))
    record_path = base/'hud.assets'; record = record_path.read_bytes()
    checks['exact_installed_payload'] = len(record) == 4642 and record[112:] == rom[0x8ec14:0x8fdc6]
    checks['prepared_digest_bound'] = digest(record_path) == build['hud_sha256']
    borrowed = C.create_string_buffer(record)
    checks['valid_record_loads'] = new.TlkMdHudAssetsLoad(borrowed, len(record)) == 1
    C.memset(borrowed, 0, len(record))
    checks['owns_its_input'] = new.TlkMdHudAssetsReady() == 1 and new.TlkMdHudAssetsActivate() == 1
    meter_count = 0
    for kind, maxima in [(0, range(16, 49)), (1, range(4, 15))]:
        for maximum in maxima:
            for current in range(maximum+1):
                a = C.create_string_buffer(704); b = C.create_string_buffer(704)
                checks[f'meter-{kind}-{maximum}-{current}'] = (old.TlkMdHudGenerate(kind, maximum, current, a, 704) == 1
                    and new.TlkMdHudGenerate(kind, maximum, current, b, 704) == 1 and a.raw == b.raw)
                meter_count += 1
    for lives in (0, 2, 8, 9, 10, 12):
        for module in (old, new): module.TlkMdHudPrepare(24, 13, 6, 3, lives)
        checks[f'life-ready-{lives}'] = old.TlkMdHudLifeReady() == new.TlkMdHudLifeReady()
        checks[f'pixels-{lives}'] = all(old.TlkMdHudPixel(kind, x, y) == new.TlkMdHudPixel(kind, x, y)
            for kind in (0, 1, 2) for y in range(-8, 32) for x in range(-2, 64))
    invalid = dict(short=record[:111], truncated=record[:-1], trailing=record+b'\0')
    for label, offset in [('magic', 0), ('version', 8), ('length', 12), ('source', 16),
                          ('start', 48), ('end', 52), ('byte_order', 56), ('reserved', 60),
                          ('digest', 80), ('payload', 112)]:
        changed = bytearray(record); changed[offset] ^= 1; invalid[label] = changed
    for label, value in invalid.items():
        raw = C.create_string_buffer(bytes(value))
        checks['reject-'+label] = new.TlkMdHudAssetsLoad(raw, len(value)) == 0
        checks['preserve-'+label] = new.TlkMdHudAssetsReady() == 1 and new.TlkMdHudAssetsActivate() == 1
    checks['null_record_rejected'] = new.TlkMdHudAssetsLoad(None, len(record)) == 0
    checks['reader_accepts_file'] = new.TlkMdHudAssetsReadFile(str(record_path).encode()) == 1
    bad_file = out/'trailing.assets'; bad_file.write_bytes(record+b'\0')
    checks['reader_rejects_trailing_file'] = new.TlkMdHudAssetsReadFile(str(bad_file).encode()) == 0
    checks['reader_rejects_missing_file'] = new.TlkMdHudAssetsReadFile(str(out/'missing.assets').encode()) == 0
    helper = base/'tool/tlk_prepare_hud_assets.exe'
    wrong = out/'wrong.md'; wrong.write_bytes(bytes(0x300000))
    target = out/'preserve.assets'; target.write_bytes(record)
    cmd = [str(helper), '--md-rom', str(wrong), '--output', str(target)]
    with (out/'wrong-source.log').open('wb') as log:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
    checks['wrong_source_preserves_target'] = rc == 4 and target.read_bytes() == record
    checks['no_staging_left'] = not list(out.glob('*.hud-install-part'))
    paths = [Path(__file__), build_path, player_path, original, patched, reader, sha, rom_path, record_path,
             ROOT/'engine/runner/tlk_md_hud_assets.h', ROOT/'engine/runner/tlk_md_hud_assets_internal.h']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  meter_states=meter_count, independent_preceding_renderer=True,
                  original_game_hud_fidelity_revalidated=False, component_serialization_parity_only=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), meter_count,
          [k for k, v in checks.items() if not v][:12], flush=True)


if __name__ == '__main__':
    main()
