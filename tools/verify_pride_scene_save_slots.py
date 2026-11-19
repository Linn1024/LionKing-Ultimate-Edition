"""Exercise actual F1/F5 on the scene-aware candidate using the prior oracle."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_preview_slots.py')
source=original.read_text().replace("ROOT/'build/pride-launch2'","ROOT/'build/pride-launch3'")
source=source.replace("base/'preview-package-audit.json'","base/'build-report.json'")
source=source.replace("ROOT/'dist/development-preview/LionKing.exe'","base/'player.exe'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
