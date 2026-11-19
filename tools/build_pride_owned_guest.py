"""Build all Pride replacement objects from maintained CMake/source generation."""
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
    parser.add_argument('--out', type=Path, default=ROOT / 'build/pride-owned-guest')
    parser.add_argument('--generation', type=Path, default=ROOT / 'build/pride-owned-guest-generation')
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'build') and not out.exists()
    out.mkdir()
    generation = args.generation.resolve()
    gp = generation / 'generation-report.json'
    g = bound(gp)
    for name, sha in g['generated_sha256'].items():
        assert digest(generation / name) == sha
    parent = ROOT / 'build/pride-owned-core'
    bp = parent / 'build-report.json'
    previous = bound(bp)
    cwd = ROOT / 'engine/build-win'
    ninja = 'C:/mingw32/bin/ninja.exe'
    rows = json.loads(subprocess.check_output([ninja, '-t', 'compdb'], cwd=cwd))
    command_for = lambda suffix: argv(next(r['command'] for r in rows if r.get('output', '').replace('\\', '/').endswith(suffix)))
    host_command = command_for('CMakeFiles/tlk_scene_prepared_sdl.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj')
    guest_command = command_for('generated/snesrecomp/bankc0_part00_v2.c.obj')
    identity = re.search(r'#define TLK_PRIDE_SAVE_COMPATIBILITY_BYTES (.+)',
                         (ROOT / 'build/pride-owned-host3/tlk_pride_save_identity.h').read_text()).group(1)
    identity = ''.join(f'{int(byte, 16):02x}' for byte in identity.split(','))
    project = out / 'project'
    project.mkdir()
    quote = lambda text: '[=[' + str(text).replace('\\', '/') + ']=]'
    text = 'cmake_minimum_required(VERSION 3.20)\nproject(PrideOwnedGuest C)\n'
    for label, command in (('host_template', host_command), ('guest_template', guest_command)):
        text += 'add_library(' + label + ' OBJECT dummy.c)\n'
        text += 'target_include_directories(' + label + ' PRIVATE ' + ' '.join(quote(v[2:]) for v in command if v.startswith('-I')) + ')\n'
        text += 'target_compile_definitions(' + label + ' PRIVATE ' + ' '.join(quote(v[2:]) for v in command if v.startswith('-D')) + ')\n'
        options = '-O3 -w -Wno-implicit-function-declaration' if label == 'guest_template' else '-O3'
        text += 'target_compile_options(' + label + ' PRIVATE ' + options + ')\n'
    for module in ('TlkPrideHost', 'TlkPrideCore', 'TlkPrideGuest'):
        text += 'include(' + quote(ROOT / ('engine/cmake/' + module + '.cmake')) + ')\n'
    text += 'tlk_add_pride_host_object(owned_host host_template ' + identity + ')\n'
    text += 'tlk_add_pride_core_objects(owned_core host_template)\n'
    text += 'tlk_add_pride_guest_objects(owned_guest guest_template ' + quote(ROOT / 'Lion King, The (USA).sfc') + ' ' + quote(generation) + ')\n'
    cmake = project / 'CMakeLists.txt'
    cmake.write_text(text)
    (project / 'dummy.c').write_text('int unused_template;\n')
    build = out / 'cmake'
    commands = [['C:/mingw32/bin/cmake.exe', '-S', str(project), '-B', str(build), '-G', 'Ninja',
                 '-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe', '-DCMAKE_MAKE_PROGRAM=' + ninja],
                ['C:/mingw32/bin/cmake.exe', '--build', str(build), '--target', 'owned_host', 'owned_core', 'owned_guest', '-j', '4']]
    with (out / 'build.log').open('wb') as log:
        for cmd in commands:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=360)
    objects = list(build.rglob('*.c.obj'))
    mapping = {}
    for old in previous['link_inputs_sha256']:
        if not old.startswith('build/'):
            continue
        if old in previous['remaining_staged_inputs_sha256']:
            name = 'bankc0_part1f_v2.c.obj' if old.endswith('/clear.obj') else Path(old).name
        else:
            name = Path(old).name
        candidates = [p for p in objects if p.name == name]
        assert len(candidates) == 1, (old, candidates)
        mapping[old] = candidates[0]
    assert len(mapping) == 28
    response = argv('response ' + (parent / 'player.rsp').read_text())[1:]
    found = set()
    for i, arg in enumerate(response):
        if not arg.lower().endswith(('.obj', '.a')):
            continue
        p = Path(arg)
        name = (p if p.is_absolute() else cwd / p).resolve().relative_to(ROOT).as_posix()
        if name in mapping:
            response[i] = mapping[name].as_posix()
            found.add(name)
    assert found == set(mapping)
    rsp = out / 'player.rsp'
    rsp.write_text(subprocess.list2cmdline(response))
    raw = subprocess.check_output([ninja, '-t', 'commands', 'tlk_scene_prepared_sdl.exe'], cwd=cwd, text=True).splitlines()[-1]
    cmd = argv(raw.split('&&', 1)[1].rsplit('&&', 1)[0].strip())
    cmd[next(i for i, arg in enumerate(cmd) if arg.startswith('@'))] = '@' + rsp.as_posix()
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
    for name, replacement in mapping.items():
        assert inputs.pop(name) == digest(ROOT / name)
        relative = replacement.relative_to(ROOT).as_posix()
        inputs[relative] = digest(replacement)
        replacements[name] = relative
    for name, sha in inputs.items():
        assert digest(ROOT / name) == sha
        assert not name.startswith('build/') or name.startswith(out.relative_to(ROOT).as_posix() + '/')
    for name in ('genesis_plus_gx_libretro.dll', 'save-compatibility.json'):
        shutil.copy2(parent / name, out / name)
    paths = [Path(__file__), bp, gp, cmake, ROOT / 'engine/cmake/TlkPrideGuest.cmake', ROOT / 'engine/scripts/validate_pride_generation.py']
    report = dict(result='BUILT', binary_sha256=digest(binary), replacements=replacements,
                  link_inputs_sha256=inputs, production_sha256=previous['production_sha256'],
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  maintained_cmake_replacement_objects=28, remaining_historical_staged_replacement_objects=0,
                  ordinary_engine_objects_and_link_template_still_reused=True,
                  public_player_enabled=False, full_first_level_fidelity_complete=False)
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('All 28 replacement objects freshly built; no historical staged replacements linked', flush=True)


if __name__ == '__main__':
    main()
