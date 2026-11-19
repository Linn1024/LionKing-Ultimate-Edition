"""Exercise the published all-MD CMD and verify the new hyena gameplay choice."""
from pathlib import Path
template=Path(__file__).with_name('verify_graveyard655_cmd.py')
s=template.read_text().replace('build/graveyard654-publication/report.json','build/graveyard689-publication/report.json').replace('build/graveyard655-cmd','build/graveyard690-installed')
s=s.replace("row['field']>=1500", "row['field']>=1650")
s=s.replace("'gameplay.levels.elephant_graveyard.vulture_bounds'", "'gameplay.levels.elephant_graveyard.vulture_bounds','gameplay.levels.elephant_graveyard.hyena_ground_tags'")
s=s.replace('paths=[Path(__file__),publication,','paths=[Path(__file__),template,publication,')
exec(compile(s,str(template),'exec'))
