"""Validate frozen evidence after the ledge-preview launcher promotion."""
from pathlib import Path

original_verifier=Path(__file__).with_name('pride_arrival_history.py')
source=original_verifier.read_text().replace("('build/pride-arrival-baseline/report.json',",
    "('build/pride-ledge-baseline/report.json','build/pride-arrival-baseline/report.json',")
needle="    for name,sha in report.get('source_sha256',{}).items():";assert source.count(needle)==1
source=source.replace(needle,"""    for launcher_archive in ('build/pride-arrival-work/player/launcher-baseline/report.json','build/pride-ledge-work/player/launcher-baseline/report.json'):
        extra=json.loads((ROOT/launcher_archive).read_text())
        candidates.setdefault('Play Standalone Preview.cmd',[]).append((extra['original_launcher_sha256'],extra['archived_launcher']))
"""+needle)
exec(compile(source,str(original_verifier),'exec'))
