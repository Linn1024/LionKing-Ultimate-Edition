"""Build a read-only observer using only the new standalone player's objects."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from build_pride_rng_allbugs import OBSERVER
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-player'
    bp = base / 'build-report.json'
    build = bound(bp)
    out = base / 'allbugs-observer'
    out.mkdir()
    ninja = 'C:/mingw32/bin/ninja.exe'
    rows = json.loads(subprocess.check_output([ninja, '-t', 'compdb', '-x'], cwd=base))
    host_row, = [r for r in rows if r.get('output', '').endswith('/tlk_pride_host.c.obj')]
    link_row, = [r for r in rows if r.get('output') == 'native-engine/tlk_pride_player.exe']
    source = out / 'observer.c'
    host_source = ROOT / 'engine/runner/pride/tlk_pride_host.c'
    source.write_text('#define __wrap_RtlRunFrame PrideObservedRunFrame\n#include "' + host_source.as_posix() +
                      '"\n#undef __wrap_RtlRunFrame\n' + OBSERVER)
    obj = out / 'host.obj'
    command = argv(host_row['command'])
    for flag, value in (('-c', source.as_posix()), ('-o', obj.as_posix()), ('-MF', obj.as_posix() + '.d'), ('-MT', obj.as_posix())):
        command[command.index(flag) + 1] = value
    with (out / 'compile.log').open('wb') as log:
        subprocess.run(command, cwd=base, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    # Ninja expands its own response content. Strip only cmd's cd/post-build
    # shell steps; production targets, sources and files are never reconfigured.
    raw = link_row['command'].split('&&', 1)[1].split('&&', 1)[0].strip()
    link = argv(raw)
    old_host = (base / host_row['output']).resolve()
    found = 0
    for i, arg in enumerate(link):
        if arg.lower().endswith('.obj'):
            p = Path(arg)
            if (p if p.is_absolute() else base / p).resolve() == old_host:
                link[i] = obj.as_posix()
                found += 1
        if arg.startswith('-Wl,--out-implib,'):
            link[i] = '-Wl,--out-implib,' + (out / 'observer.dll.a').as_posix()
    assert found == 1
    binary = out / 'player.exe'
    link[link.index('-o') + 1] = binary.as_posix()
    rsp = out / 'observer.rsp'
    rsp.write_text(subprocess.list2cmdline(link[1:]))
    with (out / 'link.log').open('wb') as log:
        subprocess.run([link[0], '@' + rsp.as_posix()], cwd=base, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    inputs = dict(build['link_inputs_sha256'])
    assert inputs.pop(old_host.relative_to(ROOT).as_posix()) == digest(old_host)
    for name, sha in inputs.items():
        assert digest(ROOT / name) == sha, name
    inputs[obj.relative_to(ROOT).as_posix()] = digest(obj)
    backend = base / 'genesis_plus_gx_libretro.dll'
    shutil.copy2(backend, out / backend.name)
    paths = [Path(__file__), ROOT / 'tools/build_pride_rng_allbugs.py', bp, source, host_source, rsp, backend]
    report = dict(result='BUILT', binary_sha256=digest(binary), link_inputs_sha256=inputs,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  all_nonhost_link_inputs_identical=True, guest_writes_added=False,
                  production_binary_unchanged=digest(base / 'player.exe') == build['binary_sha256'],
                  full_first_level_fidelity_complete=False)
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Read-only observer linked from the new standalone graph; production unchanged', flush=True)


if __name__ == '__main__':
    main()
