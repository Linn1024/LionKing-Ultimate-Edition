"""Correct the package inventory's .md/Markdown ambiguity without replaying."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-checkpoint-capability53';out=base/'package-qualification';out.mkdir()
    source=base/'package-play/report.json';prior=bound(source)
    packagepath=ROOT/'dist/installed-preview53/package-report.json';package=bound(packagepath)
    assert [k for k,v in prior['checks'].items() if not v]==['no_prepared_payloads_bundled']
    files=[p for p in packagepath.parent.rglob('*') if p.is_file()]
    markdown=[p for p in files if p.suffix.lower()=='.md']
    textfiles={p.relative_to(packagepath.parent).as_posix():p.read_text(encoding='utf-8') for p in markdown}
    checks={k:v for k,v in prior['checks'].items() if k!='no_prepared_payloads_bundled'}
    checks['markdown_files_are_textual_license_documents']=set(p.name for p in markdown)=={'README.md','NOTICE-fonts.md'} and all('\0' not in text for text in textfiles.values())
    checks['no_rom_or_prepared_payloads_bundled']=not any(p.suffix.lower() in ('.sfc','.smc','.assets','.cache') for p in files) and not any(
        p.read_bytes()[0x100:0x104]==b'SEGA' for p in markdown)
    checks['no_unrecorded_files']=set(p.relative_to(packagepath.parent).as_posix() for p in files)==set(package['artifacts_sha256'])|{'package-report.json'}
    paths=[Path(__file__),source,packagepath]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                original_suffix_check_failure_retained=True,gameplay_replayed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
