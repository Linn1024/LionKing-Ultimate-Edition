"""Prepare a fresh patched codegen copy without modifying either framework."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def main():
    engine = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    workspace_build = engine.parent / 'build'
    if not out.is_relative_to(workspace_build) or out.exists():
        parser.error('output must be a new directory under the workspace build directory')
    shutil.copytree(engine / 'snesrecomp', out,
                    ignore=shutil.ignore_patterns('.git', 'target', '__pycache__', '.pytest_cache'))
    patches = sorted((engine / 'patches/snesrecomp').glob('*.patch'))
    for patch in patches:
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=out, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=out, check=True)
    env = os.environ.copy()
    local_tools = engine.parent / '.tools'
    cargo = shutil.which('cargo')
    if not cargo and (local_tools / 'cargo/bin/cargo.exe').is_file():
        cargo = str(local_tools / 'cargo/bin/cargo.exe')
        env['CARGO_HOME'] = str(local_tools / 'cargo')
        env['RUSTUP_HOME'] = str(local_tools / 'rustup')
        env['PATH'] = str(local_tools / 'cargo/bin') + os.pathsep + env['PATH']
        if Path('C:/mingw32/bin').is_dir():
            env['PATH'] = 'C:/mingw32/bin' + os.pathsep + env['PATH']
    if not cargo:
        raise RuntimeError('cargo is required to build the patched native analyzer')
    command = [cargo, 'build', '--release', '--locked', '--offline', '--manifest-path', str(out / 'recompiler-rs/Cargo.toml')]
    subprocess.run(command, cwd=out, env=env, check=True)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(result='PREPARED', patches_sha256={p.name: digest(p) for p in patches},
                  source_sha256={str(Path(__file__).resolve()): digest(Path(__file__))}, command=command,
                  submodule_head=subprocess.check_output(['git', '-C', str(engine / 'snesrecomp'), 'rev-parse', 'HEAD'], text=True).strip())
    (out / 'pride-codegen-prepared.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, flush=True)


if __name__ == '__main__':
    main()
