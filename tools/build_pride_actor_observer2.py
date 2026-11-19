"""Build an observer that counts original pad reads for both tape modes."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text()
replacements={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-bounce-owner-work/player'",
    "out = base / 'allbugs-observer'":"out = base / 'actor-observer2'",
    'from build_pride_rng_allbugs import OBSERVER':
        "OBSERVER='#include \"'+(ROOT/'tools/native_pride_actor_observer2.c').as_posix()+'\"\\n'",
    'from summarize_pride_practice import bound':'from pride_bounce_owner_preview_history import bound',
    'paths = [Path(__file__),':
        "paths = [Path(__file__), original, ROOT/'tools/native_pride_actor_observer.c', ROOT/'tools/native_pride_actor_observer2.c',",
}
for before,after in replacements.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
