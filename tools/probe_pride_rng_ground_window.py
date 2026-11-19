"""Observe the actual earlier default-ground call and completed health/ready deadlines."""
from pathlib import Path

original_verifier=Path(__file__).with_name('reproduce_pride_rng_completion_failure.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-rng-player'","ROOT/'build/pride-rng-player2'")
source=source.replace("base/'completion-failure'","base/'ground-window'")
source=source.replace('paths=[Path(__file__),bp,profile,tape]','paths=[Path(__file__),original_verifier,bp,profile,tape]')
exec(compile(source,str(original_verifier),'exec'))
