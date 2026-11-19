"""Exercise actual F1/F5 after replacing private temporary filenames."""
from pathlib import Path

previous_verifier=Path(__file__).with_name('verify_pride_rng_private_slots.py')
source=previous_verifier.read_text().replace("ROOT/'build/pride-rng-player'", "ROOT/'build/pride-rng-player3'")
source=source.replace('paths=[Path(__file__),original_verifier,',
                      'paths=[Path(__file__),original_verifier,previous_verifier,')
exec(compile(source,str(previous_verifier),'exec'))
