"""All75 original native endpoints after output-only menu replacement."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_hyena_voice72_native75.py')
source=original.read_text().replace("ROOT/'build/pride-hyena-voice72'","ROOT/'build/pride-menu-output83'")
source=source.replace("'max_workers=3'","'max_workers=2'")
exec(compile(source,str(original),'exec'))
