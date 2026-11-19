"""Actual F1/F5 at the pre-Pride title boundary with MD behavior selected."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_preview_slots.py')
source=original.read_text().replace("ROOT/'build/pride-launch2'","ROOT/'build/pride-launch4'")
source=source.replace("base/'preview-package-audit.json'","base/'build-report.json'")
source=source.replace("ROOT/'dist/development-preview/LionKing.exe'","base/'player.exe'")
source=source.replace("base/'preview-slots'","base/'menu-slots'")
source=source.replace("'--practice-level',0,",'')
source=source.replace('1701','701').replace('1700','700').replace('1600','600').replace('1615','615')
source=source.replace("record[:8]==b'PRPRAC01'", "record[:8]==b'TLKSTAT1'")
source=source.replace('record[20:24]','record[12:16]')
source=source.replace('(field+1)*48000','field*48000')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
