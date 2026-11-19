"""Actual live independent Graveyard hyena palette selection from the current entry fixture."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/graveyard504-hyenas/report.json').replace('build/cant-wait442-ui','build/graveyard512-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.enemies.hyenas.palette')
s=s.replace("'2200'","'1801'").replace('==2200','==1801').replace('>=2250','>=1830').replace("r['level']==1","r['level']==2").replace('==0xc003b9','==0xc003eb')
s=s.replace("choices(draft)['graphics.scenery.palettes'][4]==2", "choices(draft)['graphics.scenery.palettes'][4]==1")
s=s.replace('monkey-options.png','hyena-options.png').replace('monkeys.png','hyenas.png').replace('Actual SDL second-level animal palette node','Actual SDL Graveyard hyena palette node')
s=s.replace('paths=[Path(__file__),reference]', 'paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
