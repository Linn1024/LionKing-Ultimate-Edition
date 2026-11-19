"""Generate native, hook and RNG program trees for the standalone player."""
import argparse
import hashlib
import json
import os
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
    if not out.is_relative_to(root / 'build') or out.exists():
        parser.error('output must be a new directory under the workspace build directory')
    manifest_path = engine / 'recomp/pride_hooks.json'
    manifest = json.loads(manifest_path.read_text())
    native_manifest = native_hooks.load(engine)
    rom = args.rom.resolve()
    if rom.stat().st_size != 0x300000 or digest(rom) != manifest['rom_sha256']:
        parser.error('unsupported SNES ROM identity')
    out.mkdir()
    backend = args.codegen.resolve() if args.codegen else out / 'codegen'
    if not args.codegen:
        with (out / 'prepare.log').open('wb') as log:
            subprocess.run([sys.executable, str(engine / 'scripts/prepare_pride_codegen.py'), '--out', str(backend)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    compiler = backend / 'recompiler/v2/emit_function.py'
    if 'TLK_COMPILED_TAIL_ENTRIES' not in compiler.read_text():
        raise RuntimeError('codegen lacks native continuation/tail support')
    if 'TLK_COMPILED_HOOK_POINTS' not in compiler.read_text():
        raise RuntimeError('codegen lacks the maintained optional hook patch')
    cfg = out / 'recomp'
    shutil.copytree(engine / 'recomp', cfg)
    rng_cfg = out / 'recomp-rng'
    shutil.copytree(cfg, rng_cfg)
    bank = rng_cfg / 'bankc0.cfg'
    text = bank.read_text()
    assert 'hle_func 7958' not in text
    bank.write_text(text + '\n# Original clear body with the independent scene-entry RNG seam.\nhle_func 7958 TlkRngEntryDispatch\n')
    with (out / 'header.log').open('wb') as log:
        subprocess.run([sys.executable, str(backend / 'tools/v2_sync_funcs_h.py'), '--cfg-dir', str(cfg),
                        '--out', str(cfg / 'funcs.h')], stdout=log, stderr=subprocess.STDOUT, check=True)
    clean = {k: v for k, v in os.environ.items() if k != 'TLK_COMPILED_HOOK_POINTS'}
    commands = {}
    for label, configuration, points in (('native', cfg, []), ('hooks', cfg, manifest['hook_pcs']), ('rng', rng_cfg, [])):
        destination = out / label
        env = native_hooks.environment(clean, native_manifest, label != 'rng')
        env['TLK_COMPILED_HOOK_POINTS'] = json.dumps(points)
        command = [sys.executable, str(backend / 'tools/v2_emit.py'), '--rom', str(rom), '--cfg-dir', str(configuration),
                   '--out-dir', str(destination), '--no-host-root-scan', '--cfg-roots', '--analysis-backend', 'native',
                   '--max-insns', '4096', '--max-nodes', '100000', '--bank-shard-threshold-kib', '4096', '--bank-shard-pc-span', '0x800']
        commands[label] = command
        with (out / (label + '.log')).open('wb') as log:
            subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        if label != 'rng':
            native_hooks.finish_tree(destination, native_manifest)
    hooks = sorted(p for p in (out / 'hooks').glob('bank*.c') if 'PrideSceneCompiledPreOpcode' in p.read_text())
    assert [p.name for p in hooks] == sorted(manifest['instrumented_units'])
    for path in hooks:
        # A sharded file can start before its per-function bridge declaration.
        path.write_text('#include "pride_scene_compiled_hooks_api.h"\n' + path.read_text())
    rng = out / 'rng/bankc0_part1f_v2.c'
    assert 'TlkRngEntryDispatch(cpu)' in rng.read_text() and 'PrideSceneCompiledPreOpcode' not in rng.read_text()
    original = out / 'native/program_manifest.json'
    assert json.loads(original.read_text()) == json.loads((out / 'hooks/program_manifest.json').read_text())
    paths = [engine/'recomp/pride_native_hooks.json', engine/'scripts/native_hook_generation.py', Path(__file__), engine / 'scripts/prepare_pride_codegen.py', manifest_path, compiler, rom,
             *sorted((engine / 'recomp').glob('*.cfg')), *sorted((engine / 'patches/snesrecomp').glob('*.patch'))]
    report = dict(result='GENERATED', native_hooks=native_hooks.metadata(out, native_manifest, ['native', 'hooks']), commands=commands, instrumented_units=[p.name for p in hooks],
                  source_sha256={p.relative_to(root).as_posix(): digest(p) for p in paths},
                  generated_sha256={p.relative_to(out).as_posix(): digest(p) for p in [*hooks, rng, *(out / 'native').glob('*.c'), cfg / 'funcs.h']},
                  canonical_config_or_generated_tree_modified=False, normal_hook_disabled_rng_unit=True,
                  full_first_level_fidelity_complete=False)
    for relative, sha in report['native_hooks']['files'].items():
        report['generated_sha256'][relative] = sha
    (out / 'generation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Standalone native, hook and RNG program trees generated', flush=True)


if __name__ == '__main__':
    main()
