"""Verify actual Setup prepares, preserves, repairs and publishes HUD packages."""
import ctypes as C
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-hud-assets'
    tool_path = base/'build-report.json'; tool = bound(tool_path)
    out = base/'setup-verification'; out.mkdir()
    data = out/'Game data & HUD assets'
    commands = {}
    checks = {}
    def setup(label):
        cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'scripts/Setup.ps1'),
               '-SnesRom', str(ROOT/'Lion King, The (USA).sfc'), '-MdRom', str(ROOT/'Lion King, The (World).md'),
               '-DataDirectory', str(data), '-NonInteractive']
        commands[label] = cmd
        env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
        with (out/(label+'.log')).open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=180, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label, rc, flush=True)
        return rc
    checks['first_setup'] = setup('first') == 0
    first = json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    (out/'manifest-first.json').write_text(json.dumps(first, indent=2)+'\n')
    info = first['hud_assets']; package = data/info['file']; payload = package.read_bytes()
    checks['manifest_hud_version_source'] = info['version'] == 1 and info['source'] == 'megadrive'
    checks['installed_exact_component_record'] = payload == (base/'hud.assets').read_bytes() and len(payload) == 4642
    checks['manifest_digest'] = digest(package) == info['sha256'] == tool['hud_sha256']
    checks['repeat_setup'] = setup('repeat') == 0
    second = json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    checks['repeat_same_descriptors'] = all(first[key] == second[key] for key in
        ('roms', 'scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets', 'hud_assets'))
    previous_manifest = (data/'install.json').read_bytes()
    kernel = C.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [C.c_wchar_p, C.c_uint, C.c_uint, C.c_void_p, C.c_uint, C.c_uint, C.c_void_p]
    kernel.CreateFileW.restype = C.c_void_p
    kernel.CloseHandle.argtypes = [C.c_void_p]
    handle = kernel.CreateFileW(str(package), 0x80000000, 1, None, 3, 0, None)
    assert handle not in (None, C.c_void_p(-1).value)
    try:
        checks['locked_publication_fails'] = setup('locked') != 0
        checks['locked_preserves_manifest'] = (data/'install.json').read_bytes() == previous_manifest
        checks['locked_preserves_existing_package'] = package.read_bytes() == payload
    finally:
        kernel.CloseHandle(handle)
    checks['no_failed_staging'] = not list(data.glob('*.staging'))
    checks['retry_setup'] = setup('retry') == 0
    checks['retry_same_payload'] = package.read_bytes() == payload
    corrupt = bytearray(payload); corrupt[-1] ^= 1; package.write_bytes(corrupt)
    checks['repair_setup'] = setup('repair') == 0
    checks['repair_exact_payload'] = package.read_bytes() == payload
    checks['no_partial_packages'] = not list(data.rglob('*.hud-install-part'))
    checks['distributed_helper_exact'] = digest(ROOT/'dist/PrepareHudAssets.exe') == tool['binary_sha256']
    paths = [Path(__file__), tool_path, ROOT/'scripts/Setup.ps1', ROOT/'scripts/Build.ps1',
             ROOT/'dist/PrepareHudAssets.exe', ROOT/'dist/PrepareFinalAssets.exe', ROOT/'dist/LionKing.exe']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  default_game_data_untouched=True, actual_setup_not_mocked=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
