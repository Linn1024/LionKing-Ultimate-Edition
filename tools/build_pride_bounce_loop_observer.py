"""Build a read-only original main-loop observer from the candidate graph."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-lizard-launch-work/player'")
source=source.replace("out = base / 'allbugs-observer'","out = base / 'bounce-loop-observer'")
source=source.replace('from build_pride_rng_allbugs import OBSERVER',"OBSERVER=(ROOT/'tools/native_bounce_loop_observer.c').read_text()")
source=source.replace('paths = [Path(__file__),',"paths = [Path(__file__), original, ROOT/'tools/native_bounce_loop_observer.c',")
exec(compile(source,str(original),'exec'))
