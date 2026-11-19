"""Record the standalone CMake player's actual object/source dependency graph."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base = ROOT / 'build/pride-player'
    binary = base / 'native-engine/tlk_pride_player.exe'
    assert binary.is_file()
    assert not (base / 'build-report.json').exists()
    ninja = 'C:/mingw32/bin/ninja.exe'
    inputs_text = subprocess.check_output([ninja, '-t', 'inputs', 'tlk_pride_player'], cwd=base, text=True)
    inputs = []
    for line in inputs_text.splitlines():
        p = Path(line.strip())
        p = (p if p.is_absolute() else base / p).resolve()
        if p.suffix.lower() in ('.obj', '.a'):
            assert p.is_relative_to(base), ('historical/imported build object', p)
            assert p.is_file(), p
            inputs.append(p)
    assert len(inputs) > 400, len(inputs)
    inputs_path = base / 'actual-inputs.txt'
    inputs_path.write_text(inputs_text)
    commands = base / 'actual-commands.txt'
    commands.write_text(subprocess.check_output([ninja, '-t', 'commands', 'tlk_pride_player'], cwd=base, text=True))
    rows = json.loads(subprocess.check_output([ninja, '-t', 'compdb'], cwd=base))
    objects = {p for p in inputs if p.suffix.lower() == '.obj'}
    sources = []
    source_objects = {}
    for row in rows:
        p = Path(row.get('output', ''))
        p = (p if p.is_absolute() else base / p).resolve()
        if p not in objects:
            continue
        source = Path(row['file'])
        source = (source if source.is_absolute() else base / source).resolve()
        assert source.is_file(), source
        assert not source.is_relative_to(ROOT / 'tools'), source
        assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base)), source
        sources.append(source)
        source_objects[p.relative_to(ROOT).as_posix()] = source.relative_to(ROOT).as_posix()
    assert len(source_objects) == len(objects), (len(source_objects), len(objects))
    alias = base / 'player.exe'
    shutil.copy2(binary, alias)
    shutil.copy2(binary.with_name('genesis_plus_gx_libretro.dll'), base / 'genesis_plus_gx_libretro.dll')
    contract = ROOT / 'engine/player/save-contract.json'
    shutil.copy2(contract, base / 'save-contract.json')
    c = json.loads(contract.read_text())
    assert digest(base / 'genesis_plus_gx_libretro.dll') == c['md_backend_sha256']
    maintained = [ROOT / 'engine/player' / name for name in ('CMakeLists.txt', 'deferred-player.cmake', 'windows32.cmake', 'save-contract.json')]
    maintained += [ROOT / 'engine/cmake' / (name + '.cmake') for name in ('TlkPridePlayer', 'TlkPrideHost', 'TlkPrideCore', 'TlkPrideGuest')]
    maintained += [ROOT / 'engine/scripts' / name for name in ('generate_pride_player.py', 'prepare_pride_codegen.py', 'validate_pride_generation.py')]
    maintained += [ROOT / 'engine/CMakeLists.txt', Path(__file__), inputs_path, commands,
                   ROOT / 'build/pride-player-configure2.log', ROOT / 'build/pride-player-build.log']
    paths = [*maintained, *sources]
    report = dict(result='BUILT', binary_sha256=digest(binary), actual_binary=binary.relative_to(ROOT).as_posix(),
                  link_inputs_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  production_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in sources if not p.is_relative_to(base)},
                  source_objects=source_objects, object_count=len(objects), archive_count=len(inputs) - len(objects),
                  every_object_and_archive_in_new_build=True, historical_object_or_link_template_imported=False,
                  old_special_build_dependencies=0, save_contract_identity=c['identity_sha256'],
                  public_player_enabled=False, full_first_level_fidelity_complete=False)
    (base / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Standalone CMake build audited:', len(objects), 'fresh objects;', len(inputs) - len(objects), 'fresh archives', flush=True)


if __name__ == '__main__':
    main()
