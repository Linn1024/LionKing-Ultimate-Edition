"""Actual level-select tail palette selection, live Apply and Windows presentation."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/cant-wait474-tail/report.json').replace('build/cant-wait442-ui','build/cant-wait475-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.animals.rhinos.tail.palette')
s=s.replace("'2200'","'1800'").replace('==2200','==1800').replace('>=2250','>=1830').replace('monkey-options.png','tail-options.png').replace('monkeys.png','tail.png')
s=s.replace('paths=[Path(__file__),reference]','paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
