"""Compare owned installed sprites with a separately compiled original decoder."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-sprite-assets'; build_path = base/'build-report.json'; build = bound(build_path)
    out = base/'verification'; out.mkdir()
    subprocess.run(['python', str(ROOT/'engine/scripts/apply_runtime_patches.py'), '--patches',
                    str(ROOT/'engine/cmake/game-patches'), '--snesrecomp', str(ROOT/'engine'), '--out', str(out/'game')], check=True)
    root = ROOT/'engine/runner'; sha = ROOT/'engine/snesrecomp/runner/src'
    commands = {}
    for label, source in [('original', root/'tlk_md_sprites.c'), ('prepared', out/'game/tlk_md_sprites.c')]:
        cmd = ['C:/mingw32/bin/gcc.exe', '-O2', '-shared', '-static-libgcc', '-I'+str(root), '-I'+str(sha),
               '-I'+str(ROOT/'engine/generated/resources'), str(source), str(root/'tlk_md_assets.c'), str(sha/'sha256.c'), '-o', str(out/(label+'.dll'))]
        subprocess.run(cmd, check=True); commands[label] = cmd
    old = C.CDLL(str(out/'original.dll')); new = C.CDLL(str(out/'prepared.dll'))
    for module in (old, new):
        module.TlkMdSpritesInit.argtypes = [C.c_void_p, C.c_size_t]
        module.TlkMdSpritesBindSnes.argtypes = [C.c_void_p, C.c_size_t]
        module.TlkMdSpritesBounds.argtypes = [C.c_uint, *([C.POINTER(C.c_int)]*4)]
        module.TlkMdSpritesPixel.argtypes = [C.c_uint, C.c_int, C.c_int]
        module.TlkMdSpritesCubDeathPixel.argtypes = [C.c_uint, C.c_int, C.c_int, C.c_int]
        module.TlkMdSpritesCubDeathReady.argtypes = [C.c_uint, C.c_void_p, C.c_size_t]
        module.TlkMdSpritesNpcSample.argtypes = [C.c_uint, C.c_int, C.c_int, C.c_uint, C.c_int, C.c_int, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
    new.TlkMdSpriteAssetsLoad.argtypes = [C.c_void_p, C.c_size_t]
    new.TlkMdSpriteAssetsSharedPalettes.argtypes = [C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
    snes = (ROOT/'Lion King, The (USA).sfc').read_bytes(); md = (ROOT/'Lion King, The (World).md').read_bytes()
    s = C.create_string_buffer(snes); m = C.create_string_buffer(md)
    assert old.TlkMdSpritesInit(m, len(md)) == build['mapped_count']; old.TlkMdSpritesBindSnes(s, len(snes))
    C.memset(s, 0, len(snes)); C.memset(m, 0, len(md))
    record = (base/'sprites.assets').read_bytes(); borrowed = C.create_string_buffer(record)
    checks = dict(valid_record_loads=new.TlkMdSpriteAssetsLoad(borrowed, len(record)) == 1)
    C.memset(borrowed, 0, len(record)); checks['owns_record_and_activates'] = new.TlkMdSpriteAssetsActivate() == 1
    checks['twenty_death_frames'] = old.TlkMdSpritesCubDeathAssetCount() == new.TlkMdSpritesCubDeathAssetCount() == 20
    checks['all903_maps_preserved'] = old.TlkMdSpritesCount() == new.TlkMdSpritesCount() == build['mapped_count'] == 903
    native = (C.c_uint16*16)(); external = (C.c_uint16*16)(); assert new.TlkMdSpriteAssetsSharedPalettes(native, external)
    checks['native_shared_palette'] = list(native) == list(struct.unpack_from('<16H', snes, 0x7b93))
    def color(c):
        channel = lambda shift: ((c >> shift) & 7) * 4 + (((c >> shift) & 7) >> 2)
        return channel(1) | (channel(5) << 5) | (channel(9) << 10)
    checks['md_shared_palette'] = list(external) == [color(int.from_bytes(md[0x1d78aa+i*2:0x1d78ac+i*2], 'big')) for i in range(16)]
    cgram = (C.c_uint16*256)()
    for bank, offset in enumerate((0x7b93, 0, 0x2fac7, 0, 0x2fb07, 0, 0x7d53, 0x2fb67)):
        if offset:
            for i in range(16): cgram[128+bank*16+i] = int.from_bytes(snes[offset+i*2:offset+i*2+2], 'little')
    wram = C.create_string_buffer(0x20000); C.memmove(C.addressof(wram)+0x10000, record[192+416:192+416+17792], 17792)
    at = 192+416+17792; pixels = 0; deaths = 0; roles = 0
    for index in range(build['mapped_count']):
        pose, size, death_size = struct.unpack_from('<III', record, at); at += 12+size+death_size
        bounds = []
        for module in (old, new):
            args = [C.c_int() for _ in range(4)]; assert module.TlkMdSpritesBounds(pose, *map(C.byref, args))
            bounds.append(tuple(v.value for v in args))
        checks[f'bounds-{index}'] = bounds[0] == bounds[1]
        x, y, width, height = bounds[0]
        checks[f'pixels-{index}'] = all(old.TlkMdSpritesPixel(pose, xx, yy) == new.TlkMdSpritesPixel(pose, xx, yy)
            for yy in range(y-1, y+height+1) for xx in range(x-1, x+width+1))
        pixels += (width+2)*(height+2)
        checks[f'role-{index}'] = old.TlkMdSpritesRole(pose) == new.TlkMdSpritesRole(pose)
        if death_size:
            deaths += 1
            checks[f'death-pixels-{index}'] = all(old.TlkMdSpritesCubDeathPixel(pose, xx, yy, mode) == new.TlkMdSpritesCubDeathPixel(pose, xx, yy, mode)
                for mode in (0, 1) for yy in range(y, y+height) for xx in range(x, x+width))
            checks[f'death-bank-{index}'] = old.TlkMdSpritesCubDeathReady(pose, wram, len(wram)) == new.TlkMdSpritesCubDeathReady(pose, wram, len(wram)) == 1
            wram[0x10000] = bytes([wram.raw[0x10000]^1])
            checks[f'death-bank-reject-{index}'] = old.TlkMdSpritesCubDeathReady(pose, wram, len(wram)) == new.TlkMdSpritesCubDeathReady(pose, wram, len(wram)) == 0
            wram[0x10000] = bytes([wram.raw[0x10000]^1])
        role = old.TlkMdSpritesRole(pose)
        if role:
            roles += 1; bank = next(b for b in range(8) if old.TlkMdSpritesDrawRole(pose, b) == role)
            def sample_equal():
                for frames in (0, 1):
                    for palette in (0, 1):
                        for pixel in range(16):
                            a = C.c_uint16(); b = C.c_uint16()
                            ra = old.TlkMdSpritesNpcSample(pose, x+width//2, y+height//2, pixel, frames, palette, cgram, C.byref(a))
                            rb = new.TlkMdSpritesNpcSample(pose, x+width//2, y+height//2, pixel, frames, palette, cgram, C.byref(b))
                            if (ra, a.value) != (rb, b.value): return False
                return True
            checks[f'palette-{index}'] = sample_equal()
            cgram[128+bank*16+1] ^= 1; checks[f'flash-{index}'] = sample_equal(); cgram[128+bank*16+1] ^= 1
    checks['all_record_rows_consumed'] = at == len(record) and deaths == 20
    bad = {}
    for name, offset in [('magic', 0), ('version', 8), ('header', 12), ('total', 16), ('count', 20),
                         ('snes', 24), ('md', 56), ('policy', 88), ('digest', 120), ('bank-size', 152),
                         ('death-count', 156), ('loaded-count', 160), ('reserved', 164)]:
        b = bytearray(record); b[offset] ^= 1; bad[name] = b
    for name, offset in [('pose-id', 192+416+17792), ('image-size', 192+416+17792+4), ('death-size', 192+416+17792+8), ('pixel-range', 192+416+17792+12)]:
        b = bytearray(record); b[offset] = 255 if name == 'pixel-range' else b[offset]^1
        b[120:152] = hashlib.sha256(b[192:]).digest(); bad[name] = b
    bad.update(truncated=record[:-1], trailing=record+b'\0')
    for name, value in bad.items():
        b = C.create_string_buffer(bytes(value)); checks['reject-'+name] = new.TlkMdSpriteAssetsLoad(b, len(value)) == 0
        checks['retain-'+name] = new.TlkMdSpriteAssetsReady() == 1 and new.TlkMdSpriteAssetsActivate() == 1
    new.TlkMdSpritesClear(); checks['record_survives_renderer_clear'] = new.TlkMdSpriteAssetsReady() == 1 and new.TlkMdSpriteAssetsActivate() == 1
    paths = [Path(__file__), build_path, root/'tlk_md_sprites.c', root/'tlk_md_sprite_assets.inc', root/'tlk_md_sprite_format.inc', out/'game/tlk_md_sprites.c']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  sampled_pixels=pixels, npc_poses=roles, full_renderer_coverage_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), pixels, 'pixels', [k for k, v in checks.items() if not v][:10], flush=True)


if __name__ == '__main__': main()
