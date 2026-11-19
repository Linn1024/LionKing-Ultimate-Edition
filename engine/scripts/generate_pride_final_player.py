"""Generate the optional final-scene player from the verified local ROM."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import native_hook_generation as native_hooks


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    engine = Path(__file__).resolve().parents[1]
    root = engine.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--codegen', type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(root/'build') or out.exists():
        parser.error('output must be a new directory under the workspace build directory')
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(engine/'scripts/generate_pride_player.py'),
               '--rom', str(args.rom.resolve()), '--out', str(out)]
    if args.codegen:
        command += ['--codegen', str(args.codegen.resolve())]
    subprocess.run(command, check=True)
    normal_path = out/'generation-report.json'
    normal = json.loads(normal_path.read_text())
    shutil.copyfile(normal_path, out/'base-generation-report.json')
    extension = out/'final-hook-generation'
    backend = args.codegen.resolve() if args.codegen else out/'codegen'
    subprocess.run([sys.executable, str(engine/'scripts/generate_pride_guest.py'),
                    '--rom', str(args.rom.resolve()), '--out', str(extension),
                    '--codegen', str(backend), '--final-scenes'], check=True)
    extra = json.loads((extension/'generation-report.json').read_text())
    assert extra['final_scene_hooks'] is True
    final_manifest = json.loads((engine/'recomp/pride_final_hooks.json').read_text())
    assert sorted(extra['instrumented_units']) == sorted(set(normal['instrumented_units']) |
                                                       set(final_manifest.get('instrumented_units', [])))
    assert json.loads((out/'native/program_manifest.json').read_text()) == json.loads(
        (extension/'hooks/program_manifest.json').read_text())
    for unit in extra['instrumented_units']:
        shutil.copyfile(extension/'hooks'/unit, out/'hooks'/unit)
    rng = 'rng/bankc0_part1f_v2.c'
    assert digest(out/rng) == digest(extension/rng)
    hook_text = ''.join((out/'hooks'/unit).read_text() for unit in extra['instrumented_units'])
    for pc in final_manifest['hook_pcs']:
        assert f'PrideSceneCompiledPreOpcode(cpu,0x{int(pc, 16):06X}u)' in hook_text, pc
    normal['source_sha256'].update(extra['source_sha256'])
    normal['source_sha256'][Path(__file__).relative_to(root).as_posix()] = digest(Path(__file__))
    for name in list(normal['generated_sha256']):
        normal['generated_sha256'][name] = digest(out/name)
    for unit in extra['instrumented_units']:
        normal['generated_sha256']['hooks/'+unit] = digest(out/'hooks'/unit)
    normal['instrumented_units'] = extra['instrumented_units']
    normal.update(final_scene_hooks=True, final_scene_hook_sites=final_manifest['hook_pcs'],
                  program_contract_sha256=extra['program_contract_sha256'],
                  final_generation_report_sha256=digest(extension/'generation-report.json'))
    normal['native_hooks'] = native_hooks.metadata(out, native_hooks.load(engine), ['native','hooks'])
    normal['generated_sha256'].update(normal['native_hooks']['files'])
    normal_path.write_text(json.dumps(normal, indent=2)+'\n')
    subprocess.run([sys.executable, str(engine/'scripts/validate_pride_generation.py'),
                    '--rom', str(args.rom.resolve()), '--generation', str(out)], check=True)
    print('Standalone final-scene player programs generated', flush=True)


if __name__ == '__main__':
    main()
