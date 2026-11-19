"""Validate exact frozen evidence after launch-preview promotion."""
import json
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def bound(path):
    report=json.loads(path.read_text());candidates={}
    for folder in ('pride-flight-baseline','pride-arrival-baseline',
                   'pride-ledge-baseline','pride-lizard-launch-baseline','pride-bounce-owner-baseline','pride-scene-template-baseline','pride-popup-baseline','pride-title-baseline','pride-title-work/attempt1','pride-title-work/attempt2'):
        archive=json.loads((ROOT/f'build/{folder}/report.json').read_text())
        for original,row in archive['historical_sources'].items():
            candidates.setdefault(original,[]).append((row['sha256'],row['archive']))
    for folder in ('pride-flight-player','pride-arrival-work/player',
                   'pride-ledge-work/player','pride-lizard-launch-work/player','pride-bounce-owner-work/player','pride-scene-template-work/player','pride-popup-work/player'):
        archive=json.loads((ROOT/f'build/{folder}/launcher-baseline/report.json').read_text())
        candidates.setdefault('Play Standalone Preview.cmd',[]).append(
            (archive['original_launcher_sha256'],archive['archived_launcher']))
    for name,sha in report.get('source_sha256',{}).items():
        current=ROOT/name
        if current.is_file() and digest(current)==sha:continue
        assert any(identity==sha and digest(ROOT/archive)==sha
            for identity,archive in candidates.get(name,[])),(path,name)
    for name,sha in report.get('artifacts_sha256',{}).items():
        assert digest(path.parent/name)==sha,(path,name)
    return report
