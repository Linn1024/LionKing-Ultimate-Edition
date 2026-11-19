"""Prepare original vulture collision bounds with all previously installed art/gameplay records."""
from pathlib import Path
template=Path(__file__).with_name('build_pride389_helper.py')
s=template.read_text().replace('build/pride389-cmake','build/graveyard619-helper')
s=s.replace("names+=['engine/runner/tlk_data_record.h'", "names+=['engine/generated/resources/pride_hitbox_map.h','tools/pride_hitbox_catalog.py','tools/graveyard_vulture_pairs.json','engine/runner/tlk_data_record.h'")
exec(compile(s,str(template),'exec'))
