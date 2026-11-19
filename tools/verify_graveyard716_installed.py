"""Check the delivered all-MD shortcut, new choices and real Windows client."""
from pathlib import Path
template=Path(__file__).with_name('verify_graveyard655_cmd.py')
s=template.read_text().replace('build/graveyard654-publication/report.json','build/graveyard715-publication/report.json').replace('build/graveyard655-cmd','build/graveyard717-installed')
s=s.replace("'2000','-NoPace'", "'1800'")
s=s.replace("row['field']>=1500", "row['field']>=1650")
s=s.replace("'gameplay.levels.elephant_graveyard.vulture_bounds'", "'gameplay.levels.elephant_graveyard.vulture_bounds','gameplay.levels.elephant_graveyard.hyena_ground_tags','gameplay.levels.elephant_graveyard.hyena_bounds','graphics.sprites.simba.cub.graveyard_death_motion','gameplay.simba.roar'")
s=s.replace('paths=[Path(__file__),publication,','paths=[Path(__file__),template,publication,')
exec(compile(s,str(template),'exec'))
