"""Verify observer neutrality and the complete native All Bugs route."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_player_allbugs.py')
source=original.read_text().replace("\"ROOT/'build/pride-player'\"","\"ROOT/'build/pride-arrival-work/player'\"")
source=source.replace('allbugs-standalone','allbugs-arrival2')
source=source.replace('sources=[Path(__file__),original_verifier,bp,','sources=[Path(__file__),original,original_verifier,bp,')
exec(compile(source,str(original),'exec'))
