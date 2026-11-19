"""Actual live ostrich-palette selection during the ordinary ride."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/cant-wait449-ostrich/report.json').replace('build/cant-wait442-ui','build/cant-wait450-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.animals.ostriches.palette')
s=s.replace("'2200'","'7000'").replace("==2200","==7000").replace(">=2250",">=7050").replace("='8000'","='9000'").replace('monkey-options.png','ostrich-options.png').replace('monkeys.png','ostrich.png')
s=s.replace('paths=[Path(__file__),reference]','paths=[Path(__file__),template,reference]')
s=s.replace('seconds=35','seconds=60')
exec(compile(s,str(template),'exec'))
