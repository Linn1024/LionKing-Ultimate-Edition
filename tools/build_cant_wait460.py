"""Build prepared rhino artwork and independent palettes with the current frontend."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait448.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait440'","base=ROOT/'build/cant-wait448'").replace("out=ROOT/'build/cant-wait448'","out=ROOT/'build/cant-wait460'")
s=s.replace("('wide',b['compiles']['wide'],None)]", "('wide',b['compiles']['wide'],None),('sprites',b['compiles']['sprites'],out/'game/tlk_md_sprites.c')]")
s=s.replace("'engine/runner/tlk_cw_ostrich_metadata.h',", "'engine/runner/tlk_cw_ostrich_metadata.h','engine/runner/tlk_cw_rhino_metadata.h','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/generated/resources/pride_sprite_map.h',")
exec(compile(s,str(template),'exec'))
