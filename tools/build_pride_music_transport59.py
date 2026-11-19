"""Private causal experiment: omit the injected native Music Off packet.

Both music sources intentionally remain audible. This is not a shippable mixer
or a new capability; it isolates the guest transport mutation from MD playback.
"""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-checkpoint-capability53'
    bp = base/'build-report.json'; prior = bound(bp)
    ap = ROOT/'build/pride-continue-token-behavior50/build-report.json'; audio = bound(ap)
    out = ROOT/'build/pride-music-transport59'; out.mkdir()
    cwd = ROOT/'build/pride-sprite-fresh44'
    cmd = audio['compiles']['audio'].copy()
    original = Path(cmd[cmd.index('-c')+1]); text = original.read_text()
    start = text.index('    if (music_active && pending_stop && word(0x1fbf)')
    end = text.index('    if (trace) fflush(trace);', start)
    removed = text[start:end]
    assert removed.count('g_ram[at]=1;') == 1 and removed.count('pending_stop=0;') == 1
    replacement = '    if (music_active && pending_stop) pending_stop=0; /* PRIVATE: no native stop packet. */\n'
    source = out/'audio.c'; source.write_text(text[:start]+replacement+text[end:])
    (out/'removed.txt').write_text(removed)
    for flag, value in [('-c', source), ('-o', out/'audio.obj'), ('-MT', out/'audio.obj'), ('-MF', out/'audio.d')]:
        cmd[cmd.index(flag)+1] = str(value)
    with (out/'compile.log').open('wb') as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    inputs = argv('link '+(base/'link.rsp').read_text())[1:]
    old = ROOT/'build/pride-continue-token-behavior50/audio.obj'
    indices = [i for i, p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve() == old]
    assert len(indices) == 1; inputs[indices[0]] = (out/'audio.obj').as_posix()
    rsp = out/'link.rsp'; rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '@'+str(rsp), '-o', str(out/'player.exe')],
                       cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    for name in ('genesis_plus_gx_libretro.dll', 'save-contract.json'):
        shutil.copyfile(base/name, out/name)
    linked = {(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p)
              for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj', '.a'))}
    unchanged = sum(prior['link_inputs_sha256'].get(p) == sha for p, sha in linked.items())
    assert unchanged == 321 and len(linked) == 322
    paths = [Path(__file__), bp, ap, original, source, rsp, out/'removed.txt']
    report = dict(result='BUILT', binary_sha256=digest(out/'player.exe'), compile=cmd,
                  link_inputs_sha256=linked, unchanged_inputs=unchanged,
                  public_preview_unchanged=True, dual_music_intentional=True,
                  production_mixer_or_capability=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], flush=True)


if __name__ == '__main__':
    main()
