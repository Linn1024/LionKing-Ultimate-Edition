"""Build owned host/core objects through CMake, retaining only staged guest banks."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'build/pride-owned-core')
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build') and not out.exists()
    out.mkdir()
    parent = ROOT / 'build/pride-owned-host3'
    bp = parent / 'build-report.json'
    previous = bound(bp)
    cwd = ROOT / 'engine/build-win'
    ninja = 'C:/mingw32/bin/ninja.exe'
    rows = json.loads(subprocess.check_output([ninja, '-t', 'compdb'], cwd=cwd))
    target = 'tlk_scene_prepared_sdl'
    suffix = f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row = next(r for r in rows if r.get('output', '').replace('\\', '/') == suffix)
    command = argv(row['command'])
    includes = [v[2:] for v in command if v.startswith('-I')]
    definitions = [v[2:] for v in command if v.startswith('-D')]
    identity = re.search(r'#define TLK_PRIDE_SAVE_COMPATIBILITY_BYTES (.+)',
                         (parent / 'tlk_pride_save_identity.h').read_text()).group(1)
    identity = ''.join(f'{int(byte, 16):02x}' for byte in identity.split(','))
    project = out / 'project'
    project.mkdir()
    quote = lambda text: '[=[' + str(text).replace('\\', '/') + ']=]'
    cmake = project / 'CMakeLists.txt'
    cmake.write_text('cmake_minimum_required(VERSION 3.20)\nproject(PrideOwnedCore C)\n'
                     'add_library(host_template OBJECT dummy.c)\n'
                     'target_include_directories(host_template PRIVATE ' + ' '.join(map(quote, includes)) + ')\n'
                     'target_compile_definitions(host_template PRIVATE ' + ' '.join(map(quote, definitions)) + ')\n'
                     'target_compile_options(host_template PRIVATE -O3)\n'
                     'include(' + quote(ROOT / 'engine/cmake/TlkPrideHost.cmake') + ')\n'
                     'include(' + quote(ROOT / 'engine/cmake/TlkPrideCore.cmake') + ')\n'
                     'tlk_add_pride_host_object(owned_host host_template ' + identity + ')\n'
                     'tlk_add_pride_core_objects(owned_core host_template)\n')
    (project / 'dummy.c').write_text('int unused_host_template;\n')
    build = out / 'cmake'
    commands = [['C:/mingw32/bin/cmake.exe', '-S', str(project), '-B', str(build), '-G', 'Ninja',
                 '-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe', '-DCMAKE_MAKE_PROGRAM=' + ninja],
                ['C:/mingw32/bin/cmake.exe', '--build', str(build), '--target', 'owned_host', 'owned_core', '-j', '4']]
    with (out / 'build.log').open('wb') as log:
        for cmd in commands:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    objects = list(build.rglob('*.c.obj'))
    find = lambda name: next(p for p in objects if p.name == name + '.c.obj')
    mapping = {
        'build/pride-owned-host3/host.obj': find('tlk_pride_host'),
        'build/pride-raster-state/sdl-ppu.c.obj': find('ppu'),
        'build/pride-reset/fixed4/sdl-common_rtl.obj': find('common_rtl'),
        'build/pride-reset/fixed3/sdl-interp_bridge.obj': find('interp_bridge'),
        'build/pride-rng-player/game.obj': find('tlk_game'),
        'build/pride-rng-player/state.obj': find('tlk_savestate'),
        'build/pride-rng-player/resources.obj': find('tlk_resources'),
        'build/pride-reset/fixed3/sdl-tlk_audio.obj': find('tlk_audio'),
        'build/pride-launch4/wide.obj': find('pride_launch_wide'),
        'build/pride-reset/fixed3/sdl-tlk_reset.obj': find('tlk_reset'),
        'build/pride-launch4/launch.obj': find('tlk_pride_launch'),
        'build/pride-rng-player/rng-entry.obj': find('tlk_rng_entry'),
        'build/pride-rng-player/rng-runtime.obj': find('tlk_rng_runtime'),
        'build/pride-rng-player3/temp-path.obj': find('tlk_temp_path'),
    }
    response = argv('response ' + (parent / 'player.rsp').read_text())[1:]
    found = set()
    for i, arg in enumerate(response):
        path = Path(arg)
        if arg.lower().endswith(('.obj', '.a')):
            relative = (path if path.is_absolute() else cwd / path).resolve().relative_to(ROOT).as_posix()
            if relative in mapping:
                response[i] = mapping[relative].as_posix()
                found.add(relative)
    assert found == set(mapping)
    rsp = out / 'player.rsp'
    rsp.write_text(subprocess.list2cmdline(response))
    raw = subprocess.check_output([ninja, '-t', 'commands', target + '.exe'], cwd=cwd, text=True).splitlines()[-1]
    cmd = argv(raw.split('&&', 1)[1].rsplit('&&', 1)[0].strip())
    cmd[next(i for i, a in enumerate(cmd) if a.startswith('@'))] = '@' + rsp.as_posix()
    binary = out / 'player.exe'
    cmd[cmd.index('-o') + 1] = binary.as_posix()
    for i, arg in enumerate(cmd):
        if arg.startswith('-Wl,--out-implib,'):
            cmd[i] = '-Wl,--out-implib,' + (out / 'player.dll.a').as_posix()
    cmd += ['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out / 'link.log').open('wb') as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    inputs = dict(previous['link_inputs_sha256'])
    replacements = {}
    for original, replacement in mapping.items():
        assert inputs.pop(original) == digest(ROOT / original)
        relative = replacement.relative_to(ROOT).as_posix()
        inputs[relative] = digest(replacement)
        replacements[original] = relative
    for name, sha in inputs.items():
        assert digest(ROOT / name) == sha, name
    for name in ('genesis_plus_gx_libretro.dll', 'save-compatibility.json'):
        shutil.copy2(parent / name, out / name)
    paths = [Path(__file__), bp, cmake, ROOT / 'engine/cmake/TlkPrideCore.cmake',
             ROOT / 'engine/cmake/TlkPrideHost.cmake', ROOT / 'engine/scripts/apply_runtime_patches.py']
    for folder in ('game-patches', 'runtime-patches', 'frontend-patches', 'pride-frontend-patches'):
        paths += sorted((ROOT / 'engine/cmake' / folder).glob('*.hunks'))
    paths += [p for p in (ROOT / 'engine/runner/pride').rglob('*') if p.is_file()]
    paths += [ROOT / 'engine/runner' / name for name in ('tlk_reset.c', 'tlk_pride_launch.c', 'tlk_rng_entry.c', 'tlk_rng_runtime.c', 'tlk_temp_path.c')]
    remaining = {name: sha for name, sha in inputs.items() if name.startswith('build/') and not name.startswith(out.relative_to(ROOT).as_posix() + '/')}
    assert len(remaining) == 14
    report = dict(result='BUILT', binary_sha256=digest(binary), link_inputs_sha256=inputs,
                  production_sha256=previous['production_sha256'], replacements=replacements,
                  remaining_staged_inputs_sha256=remaining, remaining_staged_nonhost_objects=14,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  public_player_enabled=False, full_first_level_fidelity_complete=False)
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Fresh CMake host + 13 runtime/helper objects linked; 14 guest-bank objects remain', flush=True)


if __name__ == '__main__':
    main()
