"""Actual live bone-platform palette Apply and persistence from the mid-level checkpoint."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/graveyard540-bones-qualified/report.json').replace('build/cant-wait442-ui','build/graveyard539-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.bones.palette')
s=s.replace("'8000'","'15000'").replace("'2200'","'14251'").replace('==2200','==14251').replace('>=2250','>=14281').replace("r['level']==1","r['level']==2").replace('==0xc003b9','==0xc003eb')
s=s.replace("choices(draft)['graphics.scenery.palettes'][4]==2", "choices(draft)['graphics.scenery.palettes'][4]==1")
s=s.replace('monkey-options.png','bone-options.png').replace('monkeys.png','bones.png').replace('Actual SDL second-level animal palette node','Actual SDL Graveyard bone-platform palette node')
s=s.replace('paths=[Path(__file__),reference]', 'paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
