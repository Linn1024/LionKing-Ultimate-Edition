"""Validate old evidence using exact source bytes archived before this renderer edit."""
import json
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def bound(path):
    report=json.loads(path.read_text())
    archive=json.loads((ROOT/'build/pride-flight-baseline/report.json').read_text())
    for name,sha in report.get('source_sha256',{}).items():
        if digest(ROOT/name)==sha:continue
        old=archive['historical_sources'].get(name)
        assert old and old['sha256']==sha and digest(ROOT/old['archive'])==sha,(path,name,'no matching archived source')
    for name,sha in report.get('artifacts_sha256',{}).items():
        assert digest(path.parent/name)==sha,(path,name)
    return report
