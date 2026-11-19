"""Compile the owned Pride host from clean sources, preserving reviewed core objects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


def main():
    parent = ROOT / 'build/pride-rng-player7'
    bp = parent / 'build-report.json'
    previous = bound(bp)
    out = ROOT / 'build/pride-owned-host3'
    out.mkdir()
    patcher = ROOT / 'engine/scripts/apply_runtime_patches.py'
    patch_sets = (ROOT / 'engine/cmake/frontend-patches', ROOT / 'engine/cmake/pride-frontend-patches')
    frontend = out / 'frontend'
    subprocess.run([sys.executable, str(patcher), '--patches', str(patch_sets[0]),
                    '--snesrecomp', str(ROOT / 'engine'), '--out', str(frontend)], check=True, timeout=60)
    final = out / 'host-frontend'
    subprocess.run([sys.executable, str(patcher), '--patches', str(patch_sets[1]),
                    '--snesrecomp', str(frontend), '--out', str(final)], check=True, timeout=60)
    for header in frontend.glob('*.h'):
        shutil.copy2(header, final / header.name)
    contract = parent / 'save-compatibility.json'
    shutil.copy2(contract, out / contract.name)
    # A relocation-only migration retains the tested contract. Exact token,
    # core-object and real replay checks must establish that claim separately.
    import re
    text = (parent / 'host.i').read_text()
    identity = re.search(r'kPrideSaveCompatibility\[32\]=\{([^}]+)\}', text).group(1)
    identity_header = out / 'tlk_pride_save_identity.h'
    identity_header.write_text('#define TLK_PRIDE_SAVE_COMPATIBILITY_BYTES ' + identity + '\n')
    cwd = ROOT / 'engine/build-win'
    ninja = 'C:/mingw32/bin/ninja.exe'
    target = 'tlk_scene_prepared_sdl'
    database = json.loads(subprocess.check_output([ninja, '-t', 'compdb'], cwd=cwd))
    suffix = f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row = next(r for r in database if r.get('output', '').replace('\\', '/') == suffix)
    host_source = ROOT / 'engine/runner/pride/tlk_pride_host.c'
    common = argv(row['command'])
    host = out / 'host.obj'
    for flag, value in (('-c', host_source.as_posix()), ('-o', host.as_posix()),
                        ('-MF', host.as_posix() + '.d'), ('-MT', host.as_posix())):
        common[common.index(flag) + 1] = value
    common += ['-I' + str(out), '-I' + str(frontend), '-DTLK_PRIVATE_COMPILED_HOOKS=1',
               '-DTLK_PRIDE_FRONTEND_SOURCE="' + (final / 'sdl_main.c').as_posix() + '"']
    preprocessed = out / 'host.i'
    command = common.copy()
    command[command.index('-c')] = '-E'
    command[command.index('-o') + 1] = preprocessed.as_posix()
    command += ['-CC']
    with (out / 'preprocess.log').open('wb') as log:
        subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    with (out / 'compile.log').open('wb') as log:
        subprocess.run(common, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    response = argv('response ' + (parent / 'player.rsp').read_text())[1:]
    original_host = parent / 'host.obj'
    assert response.count(original_host.as_posix()) == 1
    response[response.index(original_host.as_posix())] = host.as_posix()
    rsp = out / 'player.rsp'
    rsp.write_text(subprocess.list2cmdline(response))
    raw = subprocess.check_output([ninja, '-t', 'commands', target + '.exe'], cwd=cwd, text=True).splitlines()[-1]
    command = argv(raw.split('&&', 1)[1].rsplit('&&', 1)[0].strip())
    at = next(i for i, a in enumerate(command) if a.startswith('@'))
    command[at] = '@' + rsp.as_posix()
    binary = out / 'player.exe'
    command[command.index('-o') + 1] = binary.as_posix()
    for i, arg in enumerate(command):
        if arg.startswith('-Wl,--out-implib,'):
            command[i] = '-Wl,--out-implib,' + (out / 'player.dll.a').as_posix()
    command += ['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out / 'link.log').open('wb') as log:
        subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    inputs = dict(previous['link_inputs_sha256'])
    assert inputs.pop(original_host.relative_to(ROOT).as_posix()) == digest(original_host)
    for name, sha in inputs.items():
        assert digest(ROOT / name) == sha, name
    inputs[host.relative_to(ROOT).as_posix()] = digest(host)
    backend = parent / 'genesis_plus_gx_libretro.dll'
    shutil.copy2(backend, out / backend.name)
    paths = [Path(__file__), bp, patcher, host_source, identity_header, contract, backend,
             ROOT / 'engine/runner/sdl_main.c', *sorted(host_source.parent.iterdir()),
             *sorted(patch_sets[0].glob('*.hunks')), *sorted(patch_sets[1].glob('*.hunks'))]
    # Resolve all actual compiler dependencies. A historical staged source or
    # research include would be an error, not a silently retained dependency.
    dep = Path(host.as_posix() + '.d').read_text().replace('\\\n', ' ')
    dependencies = []
    for name in dep.split()[1:]:
        p = Path(name)
        p = (p if p.is_absolute() else cwd / p).resolve()
        try:
            relative = p.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        assert not relative.startswith('tools/'), relative
        assert not (relative.startswith('build/') and not relative.startswith(out.relative_to(ROOT).as_posix() + '/')), relative
        if p.is_file():
            dependencies.append(p)
    paths += dependencies
    report = dict(result='BUILT', binary_sha256=digest(binary), link_inputs_sha256=inputs,
                  production_sha256=previous['production_sha256'],
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  host_compiled_from_owned_sources=True, historical_host_include_dependencies=False,
                  preceding_nonhost_objects_unchanged=True, save_compatibility_unchanged=True,
                  full_binary_rebuild_independent_of_historical_objects=False,
                  public_player_enabled=False, full_first_level_fidelity_complete=False)
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Owned source host compiled and linked; no research/historical host includes', flush=True)


if __name__ == '__main__':
    main()
