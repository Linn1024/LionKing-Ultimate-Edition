"""Build an isolated final-life experiment from the current public graph."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text()
changes={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-bounce-owner-work/player'",
    "out = base / 'allbugs-observer'":"out = base / 'final-skip-probe'",
    'from build_pride_rng_allbugs import OBSERVER':"OBSERVER=(ROOT/'tools/pride_final_skip_probe.c').read_text()",
    'from summarize_pride_practice import bound':'from pride_bounce_owner_preview_history import bound',
    'paths = [Path(__file__),':"paths = [Path(__file__), original, ROOT/'tools/pride_final_skip_probe.c',",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
