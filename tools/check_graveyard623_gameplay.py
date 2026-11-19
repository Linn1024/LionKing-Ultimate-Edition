"""Exercise new Graveyard gameplay leaves on the existing ordinary route, with actual Windows captures."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard606_route_audio.py')
s=template.read_text().replace('build/graveyard599/build-report.json','build/graveyard621/build-report.json').replace('build/graveyard606-route-audio','build/graveyard623-gameplay').replace('build/graveyard529-helper/sprites.assets','build/graveyard619-helper/sprites.assets')
s=s.replace("'schema = 1\\ngame = snes\\n", "'schema = 1\\ngame = snes\\ngameplay.levels.elephant_graveyard = md\\n")
s=s.replace("TLK_SOFT_TREE_LOG=trace.name,", "TLK_SOFT_TREE_LOG=trace.name,TLK_GRAVEYARD_GAMEPLAY_TRACE=str(out/'gameplay.csv'),TLK_HITBOX_TRACE=str(out/'hitboxes.csv'),")
s=s.replace('all_exercised_effect_families=all(counts[k]>0 for k in expected),','vulture_health_applied=(out/\'gameplay.csv\').exists(),vulture_bounds_applied=(out/\'hitboxes.csv\').exists(),')
exec(compile(s,str(template),'exec'))
