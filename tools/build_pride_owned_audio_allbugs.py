"""Build the read-only route observer from the lizard-launch player's fresh objects."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-bounce-owner-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_bounce_owner_history import bound')
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__), original,')
exec(compile(source,str(original),'exec'))
