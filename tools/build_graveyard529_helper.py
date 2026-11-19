"""Build the native installer preparer with original vulture images and native palette5."""
from pathlib import Path
template=Path(__file__).with_name('build_pride389_helper.py')
s=template.read_text().replace('build/pride389-cmake','build/graveyard529-helper')
s=s.replace("names+=['engine/runner/tlk_data_record.h'", "names+=['engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_graveyard_enemy_metadata.h','engine/generated/resources/pride_sprite_map.h','tools/graveyard_vulture_pairs.json','tools/graveyard_sprite_catalog.py','engine/runner/tlk_data_record.h'")
exec(compile(s,str(template),'exec'))
