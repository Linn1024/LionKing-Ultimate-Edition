"""All60648 original native tracked fields after menu output ownership change."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'","ROOT/'build/pride-menu-output83'")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
