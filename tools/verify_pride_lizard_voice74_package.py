"""Actual installed candidate launcher, default game data and full route/media."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_package53.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-checkpoint-capability53'","ROOT/'build/pride-lizard-voice74'")
source=source.replace("ROOT/'dist/installed-preview53/package-report.json'","ROOT/'dist/installed-preview74/package-report.json'")
anchor="checks['no_prepared_payloads_bundled']=not any(p.suffix.lower() in ('.sfc','.smc','.md','.assets','.cache') for p in packagepath.parent.rglob('*') if p.is_file())"
assert source.count(anchor)==1
source=source.replace(anchor,"""files=[p for p in packagepath.parent.rglob('*') if p.is_file()]
    checks['no_prepared_payloads_bundled']=not any(p.suffix.lower() in ('.sfc','.smc','.assets','.cache') for p in files)
    markdown=[p for p in files if p.suffix.lower()=='.md']
    checks['markdown_are_textual_licenses']=set(p.name for p in markdown)=={'README.md','NOTICE-fonts.md'} and all('\\0' not in p.read_text(encoding='utf-8') and p.read_bytes()[0x100:0x104]!=b'SEGA' for p in markdown)
    package=bound(packagepath)
    checks['exact_package_inventory']=set(p.relative_to(packagepath.parent).as_posix() for p in files)==set(package['artifacts_sha256'])|{'package-report.json'}""")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
