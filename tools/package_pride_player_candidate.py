"""Prepare an unreleased portable payload and run it without developer DLL paths."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-player'
    bp = base / 'build-report.json'
    build = bound(bp)
    evidence = [base / name / 'report.json' for name in
                ('metadata-review', 'width-completion', 'regression', 'card-slots', 'boss-saves', 'card-saves', 'switch')]
    for path in evidence:
        r = bound(path)
        assert r['result'] == 'PASS' and all(r['checks'].values()), path
    out = base / 'portable-candidate2'
    out.mkdir()
    for source, name in ((base / 'player.exe', 'LionKing.exe'),
                         (base / 'genesis_plus_gx_libretro.dll', 'genesis_plus_gx_libretro.dll'),
                         (base / 'save-contract.json', 'save-contract.json'),
                         (ROOT / 'engine/LICENSE', 'LICENSE-port.txt'),
                         (ROOT / 'engine/snesrecomp/LICENSE', 'LICENSE-snesrecomp.txt'),
                         (ROOT / 'engine/recomp-ui/LICENSE', 'LICENSE-ui.txt'),
                         (ROOT / '.tools/genesis-plus-gx/LICENSE.txt', 'LICENSE-md-backend.txt'),
                         (ROOT / 'engine/packaging/LICENSE-NOTES.txt', 'LICENSE-NOTES.txt')):
        shutil.copy2(source, out / name)
    (out / 'README.txt').write_text('Lion King development candidate\n\nF12 opens the SNES/Mega Drive resource tree. Gameplay changes may restart\nthe level. This payload contains no ROMs; supply your verified game data.\nThe first-level fidelity audit and release integration remain unfinished.\nThe project launchers continue to use the preceding published preview.\n')
    check = base / 'portable-verification2'
    check.mkdir()
    config = check / 'host.ini'
    config.write_text('opengl = 0\nscale = 2\n')
    profile = check / 'resources.ini'
    profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\n')
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    clean['PATH'] = str(Path(os.environ['SystemRoot']) / 'System32')
    cmd = [out / 'LionKing.exe', '--rom', ROOT / 'Lion King, The (USA).sfc', '--md-rom', ROOT / 'Lion King, The (World).md',
           '--resource-profile', profile, '--config', config, '--frames', 600, '--no-pace', '--no-audio', '--no-record',
           '--dump-window', check / 'window.png']
    with (check / 'run.log').open('wb') as log:
        result = subprocess.run(list(map(str, cmd)), cwd=out, env=clean, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    text = (check / 'run.log').read_text()
    hashes = dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)', text, re.M))
    previous = ROOT / 'build/pride-reset/fixed4/native/gates/play-report.json'
    reference = json.loads(previous.read_text())['routes']['idle600']['aot']
    checks = dict(clean_path_exit=result.returncode == 0, native_idle_endpoint=hashes == reference,
                  md_backend_ready='MD audio ready' in text,
                  packaged_binary_exact=digest(out / 'LionKing.exe') == build['binary_sha256'],
                  no_rom_payload=not any(p.suffix.lower() in ('.sfc', '.smc', '.md', '.bin') for p in out.iterdir()))
    paths = [Path(__file__), bp, previous, ROOT / 'engine/runner/tlk_md_sound.c', *evidence]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=list(map(str, cmd)),
                  compared_fields=600, cleaned_path=clean['PATH'],
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(base).as_posix(): digest(p) for folder in (out, check) for p in folder.iterdir() if p.is_file()},
                  payload_publicly_installed=False, native75_release_gate_complete=False,
                  full_first_level_fidelity_complete=False)
    (base / 'portable-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
