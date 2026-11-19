"""Original whole-game tracked fields on the physical music-tail candidate."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'", "ROOT/'build/pride-music-output65'")
source=source.replace("base/'allbugs-observer'", "base/'allbugs-observer2'")
source=source.replace('paths = [Path(__file__),', 'paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
