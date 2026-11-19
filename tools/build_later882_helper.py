"""Prepare original adult-hyena/static object art and independently reviewed7/8 palettes."""
from pathlib import Path
template=Path(__file__).with_name('build_hakuna801_helper.py');s=template.read_text().replace('build/hakuna801-helper','build/later882-helper')
s=s.replace("ROOT/'tools/hakuna_sprite_catalog.py',", "ROOT/'tools/hakuna_sprite_catalog.py',ROOT/'tools/later_sprite_catalog.py',ROOT/'tools/later_actor_pairs.json',ROOT/'engine/runner/tlk_md_sprites.h',")
exec(compile(s,str(template),'exec'))
