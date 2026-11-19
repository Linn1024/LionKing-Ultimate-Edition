"""Prepare later actor images and expanded gorilla action artwork."""
from pathlib import Path
template=Path(__file__).with_name('build_hakuna801_helper.py')
s=template.read_text().replace('build/hakuna801-helper','build/hakuna814-helper')
s=s.replace("ROOT/'tools/hakuna_sprite_catalog.py',", "ROOT/'tools/hakuna_sprite_catalog.py',ROOT/'tools/hakuna_destiny_actor_pairs.json',ROOT/'engine/runner/tlk_md_sprites.h',")
exec(compile(s,str(template),'exec'))
