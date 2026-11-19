"""Prepare additional Stampede frames and both scenes' original palettes."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard683_helper.py')
s=template.read_text().replace('build/graveyard683-helper','build/next741-helper')
s=s.replace("'tools/graveyard_sprite_catalog.py'", "'tools/graveyard_sprite_catalog.py','tools/next_scene_catalog.py','tools/next_scene_pairs.json','engine/runner/tlk_next_scene_data.c','engine/runner/tlk_next_scene_data.h'")
exec(compile(s,str(template),'exec'))
