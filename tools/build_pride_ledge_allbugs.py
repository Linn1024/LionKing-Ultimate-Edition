"""Build the read-only route observer from the ledge player's fresh objects."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-ledge-work/player'")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__), original,')
exec(compile(source,str(original),'exec'))
