"""Scope capsule observation to the tracked decoder's FIRST loop entry."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text()
changes={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-bounce-owner-work/player'",
    "out = base / 'allbugs-observer'":"out = base / 'fallback-probe2'",
    'from build_pride_rng_allbugs import OBSERVER':"""OBSERVER=(ROOT/'tools/pride_template_preserve_probe.c').read_text()
needle='if(pc==0xc1cd75 && !scene_death && t && t->ready)'
assert OBSERVER.count(needle)==1
OBSERVER=OBSERVER.replace(needle,'if(pc==0xc1cd75 && scene_active && !scene_started && !scene_death && t && t->ready)')""",
    'from summarize_pride_practice import bound':'from pride_scene_template_history import bound',
    'paths = [Path(__file__),':"paths = [Path(__file__), original, ROOT/'tools/pride_template_preserve_probe.c',ROOT/'engine/runner/pride/pride_scene_template.h',ROOT/'build/pride-scene-template-baseline/report.json',",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
