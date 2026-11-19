"""Verify complete tracked native All Bugs playback and observer neutrality."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_player_allbugs.py')
source=original.read_text().replace("\"ROOT/'build/pride-player'\"","\"ROOT/'build/pride-ledge-work/player'\"")
source=source.replace('sources=[Path(__file__),original_verifier,bp,','sources=[Path(__file__),original,original_verifier,bp,')
exec(compile(source,str(original),'exec'))
