"""Validate frozen evidence against exact archived source versions after arrival edits."""
import json
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def bound(path):
    report=json.loads(path.read_text())
    candidates={}
    for name in ('build/pride-arrival-baseline/report.json','build/pride-flight-baseline/report.json'):
        archive=json.loads((ROOT/name).read_text())
        for original,row in archive['historical_sources'].items():
            candidates.setdefault(original,[]).append((row['sha256'],row['archive']))
    launcher=json.loads((ROOT/'build/pride-flight-player/launcher-baseline/report.json').read_text())
    candidates.setdefault('Play Standalone Preview.cmd',[]).append((launcher['original_launcher_sha256'],launcher['archived_launcher']))
    for name,sha in report.get('source_sha256',{}).items():
        current=ROOT/name
        if current.is_file() and digest(current)==sha:continue
        assert any(identity==sha and digest(ROOT/archive)==sha for identity,archive in candidates.get(name,[])),(path,name)
    for name,sha in report.get('artifacts_sha256',{}).items():assert digest(path.parent/name)==sha,(path,name)
    return report
