"""Build the tracked-field observer from only the fresh candidate objects."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text()
changes={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-scene-template-work/player'",
    'from summarize_pride_practice import bound':'from pride_scene_template_history import bound',
    'paths = [Path(__file__),':"paths = [Path(__file__), original,ROOT/'engine/runner/pride/pride_scene_template.h',",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
