"""Add read-only tracked-field logging around the qualified final-player wrapper."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from build_pride_rng_allbugs import OBSERVER
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-continue-token-behavior50'
    source_report = base/'build-report.json'
    previous = bound(source_report)
    out = base/'allbugs-observer'
    out.mkdir()
    cwd = ROOT/'build/pride-sprite-fresh44'
    cmd = previous['compiles']['host'].copy()
    cmd[cmd.index('-c')] = '-E'
    for flag, value in [('-o', out/'host-original.i'), ('-MF', out/'host.d'), ('-MT', out/'host.obj')]:
        cmd[cmd.index(flag)+1] = str(value)
    with (out/'preprocess.log').open('wb') as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    text = (out/'host-original.i').read_text()
    anchor = '_Bool __wrap_RtlRunFrame(uint32 inputs) {'
    assert text.count(anchor) == 1
    text = text.replace(anchor, 'static _Bool CacheObservedFinalRunFrame(uint32 inputs) {')
    text += '\n'+OBSERVER.replace('PrideObservedRunFrame(inputs)', 'CacheObservedFinalRunFrame(inputs)')
    source = out/'host.i'
    source.write_text(text)
    compile_command = previous['compiles']['host'].copy()
    for flag, value in [('-c', source), ('-o', out/'host.obj'),
                        ('-MF', out/'observer.d'), ('-MT', out/'host.obj')]:
        compile_command[compile_command.index(flag)+1] = str(value)
    with (out/'compile.log').open('wb') as log:
        subprocess.run(compile_command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    inputs = argv('link '+(base/'link.rsp').read_text())[1:]
    indices = [i for i, p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve() == base/'host.obj']
    assert len(indices) == 1
    inputs[indices[0]] = (out/'host.obj').as_posix()
    rsp = out/'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(out/'player.exe')], cwd=cwd, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=180)
    shutil.copyfile(base/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    all_inputs = {(cwd/p).resolve().relative_to(ROOT).as_posix(): digest(cwd/p)
                  for p in inputs if not p.startswith('-')}
    unchanged = sum(previous['link_inputs_sha256'].get(p) == sha for p, sha in all_inputs.items())
    assert unchanged == 321 and len(all_inputs) == 322
    paths = [Path(__file__), ROOT/'tools/build_pride_rng_allbugs.py', source_report, source,
             out/'host-original.i', out/'host.d']
    report = dict(result='BUILT', binary_sha256=digest(out/'player.exe'), preprocess=cmd,
                  compile=compile_command, nonhost_inputs_unchanged=unchanged, observer_only=True,
                  guest_register_or_memory_writes=False, link_inputs_sha256=all_inputs,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], 'nonhost unchanged', unchanged, flush=True)


if __name__ == '__main__':
    main()
