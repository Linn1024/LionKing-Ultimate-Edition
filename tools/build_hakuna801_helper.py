"""Prepare gorilla images and scene5/6 palettes with the maintained native helper."""
from pathlib import Path
template=Path(__file__).with_name('build_pride389_helper.py')
s=template.read_text().replace('build/pride389-cmake','build/hakuna801-helper')
s=s.replace("paths=[Path(__file__),", "paths=[Path(__file__),template,ROOT/'engine/runner/tlk_next_scene_data.c',ROOT/'engine/runner/tlk_md_sprites.c',ROOT/'engine/generated/resources/pride_sprite_map.h',ROOT/'tools/hakuna_gorilla_pairs.json',ROOT/'tools/hakuna_sprite_catalog.py',")
exec(compile(s,str(template),'exec'))
