"""Ordinary mixed-source6000-field completion after lizard sound correction."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_music_completion62.py')
source=original.read_text().replace("ROOT/'build/pride-music-output62'","ROOT/'build/pride-lizard-voice74'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
