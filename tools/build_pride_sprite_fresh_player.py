"""Generate and build a fresh final-player graph including installed sprite loading."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest


def main():
    out = ROOT/'build/pride-sprite-fresh44'
    out.mkdir()
    codegen = ROOT/'build/pride-bounce-owner-work/game-program/codegen'
    assert (codegen/'recompiler/v2/emit_function.py').exists()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['CARGO_HOME'] = str(ROOT/'.tools/cargo')
    env['RUSTUP_HOME'] = str(ROOT/'.tools/rustup')
    env['PATH'] = str(ROOT/'.tools/cargo/bin')+';'+env['PATH']
    commands = {}
    phases = [
        ('generation', [sys.executable, str(ROOT/'engine/scripts/generate_pride_final_player.py'),
                        '--rom', str(ROOT/'Lion King, The (USA).sfc'), '--out', str(out/'game-program'), '--codegen', str(codegen)]),
        ('configure', ['cmake', '-S', str(ROOT/'engine/player-final'), '-B', str(out), '-G', 'Ninja',
                       '-C', str(ROOT/'engine/player/windows32.cmake'), '-DCMAKE_BUILD_TYPE=Release',
                       '-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe', '-DCMAKE_CXX_COMPILER=C:/mingw32/bin/g++.exe',
                       '-DCMAKE_RC_COMPILER=C:/mingw32/bin/windres.exe', '-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe',
                       '-DPython3_EXECUTABLE='+sys.executable,
                       '-DTLK_PRIDE_ROM='+str(ROOT/'Lion King, The (USA).sfc'), '-DTLK_PRIDE_GENERATION='+str(out/'game-program')]),
        ('build', ['cmake', '--build', str(out), '--target', 'tlk_pride_final_player', 'tlk_prepare_hud_assets', 'tlk_prepare_sprite_assets', '-j', '6'])]
    for label, command in phases:
        commands[label] = command
        print(label, 'started', flush=True)
        with (out/(label+'.log')).open('wb') as log:
            rc = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=3600, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label, rc, flush=True)
        if rc:
            (out/'failure.json').write_text(json.dumps(dict(result='FAILED', phase=label, exit=rc, commands=commands), indent=2)+'\n')
            return
    rows = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe', '-t', 'compdb', '-x'], cwd=out))
    link_rows = [r for r in rows if r.get('output', '').replace('\\', '/') == 'native-engine/tlk_pride_final_player.exe']
    assert len(link_rows) == 1
    raw = link_rows[0]['command'].split('&&', 1)[1].split('&&', 1)[0].strip()
    arguments = argv(raw)[1:]
    i = arguments.index('-o'); del arguments[i:i+2]
    arguments = [a for a in arguments if not a.startswith('-Wl,--out-implib,')]
    rsp = out/'link.rsp'; rsp.write_text(subprocess.list2cmdline(arguments))
    inputs = {}
    for value in arguments:
        if not value.startswith('-') and value.lower().endswith(('.obj', '.a')):
            path = (out/value).resolve()
            assert path.is_relative_to(out), ('nonfresh explicit link input', str(path))
            inputs[path.relative_to(ROOT).as_posix()] = digest(path)
    assert len(inputs) > 300
    paths = [Path(__file__), ROOT/'engine/CMakeLists.txt', ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
             out/'game-program/generation-report.json', rsp]
    for row in rows:
        output = (out/row.get('output', '')).resolve()
        path = Path(row.get('file', ''))
        if not path.is_absolute(): path = out/path
        path = path.resolve()
        if output.is_file() and path.is_file() and path.is_relative_to(ROOT): paths.append(path)
    paths += sorted((ROOT/'engine/cmake/game-patches').glob('*.hunks'))
    paths += sorted((ROOT/'engine/cmake/final-frontend-patches').glob('*.hunks'))
    for name in ('tlk_pride_final_player.exe', 'genesis_plus_gx_libretro.dll', 'save-contract.json'):
        shutil.copyfile(out/'native-engine'/name, out/('player.exe' if name.endswith('_player.exe') else name))
    report = dict(result='BUILT', binary_sha256=digest(out/'player.exe'), commands=commands,
                  fresh_standalone_graph_claimed=True, old_objects_or_archives_imported=False,
                  reused_patched_codegen_tree=codegen.relative_to(ROOT).as_posix(), link_inputs_sha256=inputs,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in set(paths)})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], 'fresh inputs', len(inputs), flush=True)


if __name__ == '__main__':
    main()
