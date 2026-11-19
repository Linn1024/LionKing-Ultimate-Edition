"""Exercise actual F1/F5 with independent MD seed and MD death both selected."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_preview_slots.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch2'","ROOT/'build/pride-rng-player'")
source=source.replace("base/'preview-package-audit.json'","base/'build-report.json'")
source=source.replace("ROOT/'dist/development-preview/LionKing.exe'","base/'player.exe'")
source=source.replace("base/'preview-slots'","base/'rng-private-slots'")
old="profile.write_bytes((ROOT/'profiles/pride-development-preview.ini').read_bytes())"
assert source.count(old)==1
source=source.replace(old,"profile.write_bytes((ROOT/'profiles/pride-development-preview.ini').read_bytes()+b'\\ngameplay.levels.pride_lands.random_entry = md\\n')")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
