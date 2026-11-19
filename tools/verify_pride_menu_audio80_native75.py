"""All75 original native endpoint pairs after caller-specific menu audio."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_voice72_native75.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-hyena-voice72'","ROOT/'build/pride-menu-audio80'")
exec(compile(source,str(verifier_source),'exec'))
