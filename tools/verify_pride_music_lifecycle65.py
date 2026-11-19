"""Fresh lifecycle qualification after retaining verified physical music tails."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_music_lifecycle62.py')
source=original.read_text().replace("ROOT/'build/pride-music-output62'", "ROOT/'build/pride-music-output65'")
source=source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
