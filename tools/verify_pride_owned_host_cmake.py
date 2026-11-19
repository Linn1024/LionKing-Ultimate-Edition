"""Build the owned host through its CMake module and compare code/data to the oracle."""
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-owned-host3'
    bp = base / 'build-report.json'
    bound(bp)
    out = base / 'cmake-host'
    out.mkdir()
    project = out / 'project'
    project.mkdir()
    cwd = ROOT / 'engine/build-win'
    ninja = 'C:/mingw32/bin/ninja.exe'
    rows = json.loads(subprocess.check_output([ninja, '-t', 'compdb'], cwd=cwd))
    suffix = 'CMakeFiles/tlk_scene_prepared_sdl.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row = next(r for r in rows if r.get('output', '').replace('\\', '/') == suffix)
    command = argv(row['command'])
    includes = [v[2:] for v in command if v.startswith('-I')]
    definitions = [v[2:] for v in command if v.startswith('-D')]
    identity = re.search(r'kPrideSaveCompatibility\[32\]=\{([^}]+)\}',
                         (ROOT / 'build/pride-rng-player7/host.i').read_text()).group(1)
    identity = ''.join(f'{int(byte, 16):02x}' for byte in identity.split(','))
    quote = lambda s: '[=[' + s.replace('\\', '/') + ']=]'
    cmake = project / 'CMakeLists.txt'
    cmake.write_text('cmake_minimum_required(VERSION 3.20)\nproject(PrideHostVerification C)\n'
                     'add_library(host_template OBJECT dummy.c)\n'
                     'target_include_directories(host_template PRIVATE ' + ' '.join(map(quote, includes)) + ')\n'
                     'target_compile_definitions(host_template PRIVATE ' + ' '.join(map(quote, definitions)) + ')\n'
                     'target_compile_options(host_template PRIVATE -O3)\n'
                     'include(' + quote(str(ROOT / 'engine/cmake/TlkPrideHost.cmake')) + ')\n'
                     'tlk_add_pride_host_object(owned_host host_template ' + identity + ')\n')
    (project / 'dummy.c').write_text('int unused_host_template;\n')
    build = out / 'build'
    commands = [
        ['C:/mingw32/bin/cmake.exe', '-S', str(project), '-B', str(build), '-G', 'Ninja',
         '-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe', '-DCMAKE_MAKE_PROGRAM=' + ninja],
        ['C:/mingw32/bin/cmake.exe', '--build', str(build), '--target', 'owned_host'],
    ]
    with (out / 'build.log').open('wb') as log:
        for cmd in commands:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    obj, = build.rglob('tlk_pride_host.c.obj')
    checks = {}
    for section in ('.text', '.data', '.rdata', '.text.unlikely', '.text.startup'):
        files = []
        for label, source in (('reference', base / 'host.obj'), ('cmake', obj)):
            path = out / (label + section + '.bin')
            subprocess.run(['C:/mingw32/bin/objcopy.exe', '-O', 'binary', '--only-section=' + section,
                            str(source), str(path)], check=True, timeout=30)
            files.append(path.read_bytes())
        checks[section + '/all_bytes'] = bool(files[0]) and files[0] == files[1]
    relocations = []
    for source in (base / 'host.obj', obj):
        text = subprocess.check_output(['C:/mingw32/bin/objdump.exe', '-r', str(source)], text=True, timeout=30)
        relocations.append('\n'.join(line for line in text.splitlines() if 'file format pe-i386' not in line).strip())
    checks['all_relocation_records'] = bool(relocations[0]) and relocations[0] == relocations[1]
    paths = [Path(__file__), bp, ROOT / 'engine/cmake/TlkPrideHost.cmake',
             ROOT / 'engine/runner/pride/README.md', obj, cmake, out / 'build.log']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  historical_host_object_linked=False, whole_player_independently_built=False,
                  full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
