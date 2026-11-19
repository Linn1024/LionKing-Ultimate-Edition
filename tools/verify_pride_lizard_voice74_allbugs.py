"""All60648 original native tracked fields on the lizard sound candidate."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'","ROOT/'build/pride-lizard-voice74'")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
