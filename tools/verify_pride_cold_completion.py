"""Repeat complete ordinary routes on the pre-Pride menu-save candidate."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_launch_completion.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-launch4'")
source=source.replace("base/'completion'","base/'completion2'")
source=source.replace('sources=[Path(__file__),bp]','sources=[Path(__file__),original_verifier,bp]')
exec(compile(source,str(original_verifier),'exec'))
