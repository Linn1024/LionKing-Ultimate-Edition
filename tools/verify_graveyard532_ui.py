"""Live vulture palette switching in the actual current vulture section."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/graveyard531-vultures/report.json').replace('build/cant-wait442-ui','build/graveyard532-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.enemies.vultures.palette')
s=s.replace("'8000'","'16000'").replace("'2200'","'15001'").replace('==2200','==15001').replace('>=2250','>=15031').replace("r['level']==1","r['level']==2").replace('==0xc003b9','==0xc003eb')
s=s.replace("choices(draft)['graphics.scenery.palettes'][4]==2", "choices(draft)['graphics.sprites.enemies.vultures.frames'][4]==1")
s=s.replace('monkey-options.png','vulture-options.png').replace('monkeys.png','vultures.png').replace('Actual SDL second-level animal palette node','Actual SDL Graveyard vulture palette node')
s=s.replace('paths=[Path(__file__),reference]', 'paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
