"""Build the existing native preparer with the reviewed rhino sprite metadata."""
from pathlib import Path
template=Path(__file__).with_name('build_pride389_helper.py')
s=template.read_text().replace('build/pride389-cmake','build/cant-wait459-helper')
s=s.replace("names+=['engine/runner/tlk_data_record.h'", "names+=['engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_cw_rhino_metadata.h','engine/generated/resources/pride_sprite_map.h','tools/cw_rhino_pairs.json','tools/cw_sprite_catalog.py','engine/runner/tlk_data_record.h'")
exec(compile(s,str(template),'exec'))
