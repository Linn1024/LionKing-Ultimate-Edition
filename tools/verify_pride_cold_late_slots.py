"""Retain actual Pride and non-Pride F1/F5 after adding pristine menu saves."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_preview_slots.py')
for level in (0,1):
    source=original_verifier.read_text().replace("ROOT/'build/pride-launch2'","ROOT/'build/pride-launch4'")
    source=source.replace("base/'preview-package-audit.json'","base/'build-report.json'")
    source=source.replace("ROOT/'dist/development-preview/LionKing.exe'","base/'player.exe'")
    source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
    if level:
        source=source.replace("base/'preview-slots'","base/'native-slots'")
        source=source.replace("'--practice-level',0", "'--practice-level',1")
        source=source.replace("record[:8]==b'PRPRAC01'", "record[:8]==b'TLKSTAT1'")
        source=source.replace('record[20:24]','record[12:16]')
    exec(compile(source,str(original_verifier),'exec'))
