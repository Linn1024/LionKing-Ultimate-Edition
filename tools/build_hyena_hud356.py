"""Rebuild only the renderer's ownership latch on unchanged OAM reuploads."""
from pathlib import Path
template356=Path(__file__).with_name('build_level_caption343.py')
source=template356.read_text().replace("base=ROOT/'build/pride-porcupine327'","base=ROOT/'build/level-caption349'")
source=source.replace('level-caption343','hyena-hud356')
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template356,bp,')
source=source.replace('Later main-level falling titles centred per line; native glyph art, palette, animation and guest state retained. Pride independent caption renderer unchanged.','Retain object/HUD provenance when an empty draw list reuploads the exact displayed OAM. Actual clear/changed uploads retain the original replacement behavior; no guest or save schema changes.')
exec(compile(source,str(template356),'exec'))
