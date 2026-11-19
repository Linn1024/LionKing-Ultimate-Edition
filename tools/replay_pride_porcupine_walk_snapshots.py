"""Reproduce walking fixture snapshots from power-on with the original LLE path."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-porcupine-walk-snapshot-replay'
    out.mkdir()
    frames = (2892, 2940, 2980, 3060)
    old_path = ROOT/'build/native-pickup-flight/report.json'
    # The old analyzer source changed later; do not present it as currently bound.
    # Fresh original execution below supplies independent snapshot provenance.
    old = json.loads(old_path.read_text())
    fixtures_path = ROOT/'build/pride-porcupine-walk-originals/report.json'
    bound(fixtures_path)
    exe = ROOT/'engine/build-win/tlk_headless.exe'
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    rom = ROOT/'Lion King, The (USA).sfc'
    read_rom(rom.name, '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    command = list(map(str, [exe, '--rom', rom, '--input-polled', tape, '--frames', max(frames), '--lle']))
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env.update(TLK_WRAM_DUMP=','.join(map(str, frames)), TLK_WRAM_DIR=str(out))
    with (out/'run.log').open('wb') as log:
        run = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                             timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
    checks = dict(original_lle_exited=run.returncode == 0,
                  original_capture_binary_unchanged=digest(exe) == old['source_sha256'][exe.relative_to(ROOT).as_posix()],
                  original_capture_tape_unchanged=digest(tape) == old['source_sha256'][tape.relative_to(ROOT).as_posix()])
    paths = [Path(__file__), exe, tape, rom, old_path, fixtures_path]
    for frame in frames:
        name = f'hl_wram_{frame}.bin'
        old_snapshot = old_path.parent/name
        paths.append(old_snapshot)
        checks[f'field{frame}_fresh_matches_retained'] = digest(out/name) == digest(old_snapshot)
        checks[f'field{frame}_matches_original_recorded_digest'] = digest(out/name) == old['artifacts_sha256'][name]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=command,
                  ordinary_poweron_original_inputs=True, guest_or_rom_edits=False,
                  old_analyzer_source_currently_bound=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks),
          [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
