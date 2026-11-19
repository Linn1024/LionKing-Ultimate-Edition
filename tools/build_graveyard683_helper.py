"""Prepare socket art and Graveyard hyena ground tags using installed ROMs."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard619_helper.py')
s=template.read_text().replace('build/graveyard619-helper','build/graveyard683-helper')
s=s.replace("'engine/generated/resources/pride_hitbox_map.h'", "'engine/generated/resources/pride_sprite_map.h','engine/runner/tlk_graveyard_data.c','engine/runner/tlk_graveyard_data.h','tools/graveyard_sprite_catalog.py','engine/generated/resources/pride_hitbox_map.h'")
exec(compile(s,str(template),'exec'))
