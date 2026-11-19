"""Retain full owned-reset comparisons with the corrected field phase."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_machine_player.py')
source=original_verifier.read_text().replace("base=ROOT/'build/pride-machine-player'","base=ROOT/'build/pride-machine-player4'")
source=source.replace("stems=read_rows(folder/'stems.csv');", "stems=[r for r in read_rows(folder/'stems.csv') if r['frame'].isdigit()];")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
