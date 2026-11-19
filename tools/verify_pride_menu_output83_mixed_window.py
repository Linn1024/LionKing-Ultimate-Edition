"""Familiar Mixed Graphics shortcut and its independent native-audio defaults."""
from pathlib import Path
original=Path(__file__).with_name('capture_pride_mixed_launcher66.py')
source=original.read_text().replace("ROOT/'build/pride-launchers66'","ROOT/'build/pride-menu-output83'")
source=source.replace("source=base/'report.json'","source=base/'publication/report.json'")
source=source.replace("out=base/'windows'","out=base/'mixed-window'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
