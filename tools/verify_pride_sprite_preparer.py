"""Check installer-only sprite preparation rejects bad sources atomically."""
import json
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-sprite-assets'
    report_path = base/'build-report.json'
    build = bound(report_path)
    out = base/'preparer-verification'; out.mkdir()
    tool = base/'tool/tlk_prepare_sprite_assets.exe'
    snes = ROOT/'Lion King, The (USA).sfc'; md = ROOT/'Lion King, The (World).md'
    original = {p: digest(p) for p in (snes, md)}
    output = out/'Prepared sprites & palettes.assets'
    sentinel = b'preserve old published data'
    output.write_bytes(sentinel)
    wrong = out/'wrong.sfc'; wrong.write_bytes(bytes(0x300000))
    short = out/'short.md'; short.write_bytes(b'bad')
    commands = {}; checks = {}
    for label, s, m in [('wrong-snes', wrong, md), ('wrong-md', snes, wrong),
                        ('short-md', snes, short), ('missing-snes', out/'missing.sfc', md)]:
        cmd = [str(tool), '--snes-rom', str(s), '--md-rom', str(m), '--output', str(output)]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        commands[label] = cmd
        (out/(label+'.log')).write_bytes(result.stdout+result.stderr)
        checks[label] = result.returncode == 4 and output.read_bytes() == sentinel
    cmd = [str(tool), '--snes-rom', str(snes), '--md-rom', str(md), '--output', str(output)]
    commands['valid'] = cmd
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    (out/'valid.log').write_bytes(result.stdout+result.stderr)
    checks['valid_atomic_replacement'] = result.returncode == 0 and digest(output) == build['package_sha256']
    checks['sources_unchanged'] = all(digest(p) == sha for p, sha in original.items())
    checks['no_partials'] = not list(out.glob('*.sprite-install-part*'))
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in (Path(__file__), report_path, tool)},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), flush=True)


if __name__ == '__main__': main()
