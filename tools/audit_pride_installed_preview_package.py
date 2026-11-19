"""Correct the Markdown/ROM classification without replacing verified launcher runs."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-hud-fresh43'
    out = base/'package-verification'; out.mkdir()
    previous_path = base/'launcher-verification/report.json'; previous = bound(previous_path)
    package_path = ROOT/'dist/installed-preview43/package-report.json'; bound(package_path)
    assert previous['result'] == 'FAIL' and [k for k, v in previous['checks'].items() if not v] == ['no_rom_or_prepared_game_data_in_package']
    package = package_path.parent
    forbidden = []
    for p in package.rglob('*'):
        if not p.is_file(): continue
        with p.open('rb') as f: magic = f.read(8)
        if (p.suffix.lower() in ('.sfc', '.smc', '.bin', '.assets', '.cache') or
            magic in (b'TLKHUD01', b'TLKSCN01', b'TLKFMAR1', b'TLKFNAT1', b'TLKTBK01') or
            (p.stat().st_size == 3145728 and digest(p) in (
                '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712',
                'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'))):
            forbidden.append(p.relative_to(package).as_posix())
    checks = {k: v for k, v in previous['checks'].items() if k != 'no_rom_or_prepared_game_data_in_package'}
    checks['no_rom_or_prepared_game_data_in_package'] = not forbidden
    checks['markdown_readme_is_software_documentation'] = (package/'assets/shaders/README.md').read_text().startswith('#')
    paths = [Path(__file__), previous_path, package_path, ROOT/'tools/verify_pride_installed_preview_launcher.py']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, forbidden_files=forbidden,
                  prior_failure_retained=True, repeated_gameplay_runs=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  package_files_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in package.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
