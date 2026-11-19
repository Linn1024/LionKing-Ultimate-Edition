"""Validate frozen prior evidence against exact pre-ledge source archives."""
from pathlib import Path

original=Path(__file__).with_name('pride_arrival_history.py')
source=original.read_text().replace("('build/pride-arrival-baseline/report.json',",
    "('build/pride-ledge-baseline/report.json','build/pride-arrival-baseline/report.json',")
needle="    for name,sha in report.get('source_sha256',{}).items():";assert source.count(needle)==1
source=source.replace(needle,"""    arrival_path=ROOT/'build/pride-arrival-work/player/launcher-baseline/report.json'
    arrival=json.loads(arrival_path.read_text())
    candidates.setdefault('Play Standalone Preview.cmd',[]).append((arrival['original_launcher_sha256'],arrival['archived_launcher']))
"""+needle)
exec(compile(source,str(original),'exec'))
