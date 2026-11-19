"""Read-only tracked-field host for the entry-once hyena voice candidate."""
from pathlib import Path
original=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'","ROOT/'build/pride-hyena-voice72'")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
