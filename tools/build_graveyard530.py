"""Build independent original vulture artwork and colors in the owned Graveyard scene."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard493.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait482'","base=ROOT/'build/graveyard503'").replace("out=ROOT/'build/graveyard493'","out=ROOT/'build/graveyard530'")
s=s.replace("('wide',b['compiles']['wide'],None)]", "('wide',b['compiles']['wide'],None),('sprites',b['compiles']['sprites'],out/'game/tlk_md_sprites.c')]")
s=s.replace("'engine/runner/tlk_wide.c',", "'engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_graveyard_enemy_metadata.h','engine/generated/resources/pride_sprite_map.h','tools/graveyard_vulture_pairs.json','tools/graveyard_sprite_catalog.py',")
s=s.replace('Shared prepared cub HUD renderer enabled in owned Elephant Graveyard scene; independent component choices retained. Resources/compositor only; gameplay, audio, assets and save schema unchanged.', 'Prepared original vulture frames and independent colors in owned Graveyard actors; native timing/gameplay retained. Existing HUD, hyenas and earlier levels retained; no audio/save-schema change.')
exec(compile(s,str(template),'exec'))
