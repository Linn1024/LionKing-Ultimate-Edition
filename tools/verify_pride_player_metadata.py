"""Review the single generated build-identifier difference in all 305 objects."""
import hashlib
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-player'
    raw_path = base / 'code-equivalence2/report.json'
    raw = bound(raw_path)
    assert raw['result'] == 'FAIL' and len(raw['checks']) == 915 and len(raw['objects']) == 305
    failures = [key for key, value in raw['checks'].items() if not value]
    assert failures == ['124/all_section_bytes'], failures
    entry = raw['objects']['124']
    assert entry['differing_sections'] == ['.rdata'] and entry['old_sections'] == entry['new_sections']
    old_source = ROOT / 'engine/generated/snesrecomp/module_v2.c'
    new_source = base / 'game-program/native/module_v2.c'
    old, new = old_source.read_text(), new_source.read_text()
    pattern = r'g_program_module.build_digest = "([0-9a-f]{64})";'
    a, b = re.search(pattern, old).group(1), re.search(pattern, new).group(1)
    assert a != b and new.replace(b, a) == old
    section = hashlib.sha256(b'.rdata').hexdigest()[:16]
    old_bytes = (base / ('code-equivalence2/124-old' + section + '.bin')).read_bytes()
    new_bytes = (base / ('code-equivalence2/124-new' + section + '.bin')).read_bytes()
    assert old_bytes.count(a.encode()) == new_bytes.count(b.encode()) == 1
    checks = dict(complete_305_object_comparison=True, all_305_section_sizes_exact=True,
                  all_305_relocation_sets_exact=True, other_304_object_bytes_exact=True,
                  module_source_only_build_identifier_changed=True,
                  module_rdata_only_64_identifier_bytes_changed=new_bytes.replace(b.encode(), a.encode()) == old_bytes,
                  module_program_digest_unchanged=re.search(r'program_digest = "([^"]+)"', old).group(1) ==
                    re.search(r'program_digest = "([^"]+)"', new).group(1))
    paths = [Path(__file__), raw_path, old_source, new_source,
             ROOT / 'engine/snesrecomp/runner/src/common_cpu_infra.c']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  raw_identical_checks=914, raw_reviewed_metadata_difference_checks=1,
                  old_build_identifier=a, new_build_identifier=b,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  full_first_level_fidelity_complete=False)
    out = base / 'metadata-review'
    out.mkdir()
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], '914 identical checks; exact 64-byte build identifier change reviewed', flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
