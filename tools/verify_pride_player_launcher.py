"""Exercise the actual standalone launcher and its separate settings/data paths."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-player'
    bp = base / 'build-report.json'
    bound(bp)
    out = base / 'launcher-verification'
    out.mkdir()
    launcher = ROOT / 'Play Standalone Preview.cmd'
    cmd = [os.environ['COMSPEC'], '/d', '/c', str(launcher), '--frames', '600', '--no-pace',
           '--no-audio', '--no-record', '--dump-window', str(out / 'window.png')]
    with (out / 'run.log').open('wb') as log:
        result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    text = (out / 'run.log').read_text()
    hashes = dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)', text, re.M))
    previous = ROOT / 'build/pride-reset/fixed4/native/gates/play-report.json'
    reference = json.loads(previous.read_text())['routes']['idle600']['aot']
    checks = dict(batch_exit=result.returncode == 0, native_idle_endpoint=hashes == reference,
                  md_audio_and_graphics_ready='Pride Lands graphics ready; MD audio ready' in text,
                  no_forced_practice_start='--practice-level' not in launcher.read_text(),
                  separate_settings_exist=(ROOT / 'settings/standalone-preview/game.ini').is_file() and
                    (ROOT / 'settings/standalone-preview/resources.ini').is_file(),
                  previous_preview_unchanged=digest(ROOT / 'dist/development-preview/LionKing.exe') ==
                    digest(ROOT / 'build/pride-launch2/player.exe'))
    snapshots = []
    for name in ('game.ini', 'resources.ini'):
        source = ROOT / 'settings/standalone-preview' / name
        target = out / name
        target.write_bytes(source.read_bytes())
        snapshots.append(target)
    paths = [Path(__file__), launcher, bp, previous, ROOT / 'profiles/pride-development-preview.ini', *snapshots]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
                  compared_fields=600, installed_cache_used='resource_cache=loaded' in text,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
                  published_preview_replaced=False, full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
