"""Retain complete-route behavior after admitting earlier valid grounding."""
from pathlib import Path

previous_verifier=Path(__file__).with_name('verify_pride_rng_completion.py')
source=previous_verifier.read_text().replace("ROOT/'build/pride-rng-player'","ROOT/'build/pride-rng-player2'")
source=source.replace('sources=[Path(__file__),original_verifier,bp]','sources=[Path(__file__),original_verifier,previous_verifier,bp]')
exec(compile(source,str(previous_verifier),'exec'))
