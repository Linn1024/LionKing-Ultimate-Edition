"""Actual direct-selected rhino area: live frame source with native palette retained."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait442_ui.py')
s=template.read_text().replace('build/cant-wait441-monkeys/report.json','build/cant-wait462-rhino/report.json').replace('build/cant-wait442-ui','build/cant-wait463-ui').replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.animals.rhinos.frames')
s=s.replace("'2200'","'1800'").replace('==2200','==1800').replace('>=2250','>=1830').replace('monkey-options.png','rhino-options.png').replace('monkeys.png','rhino.png')
s=s.replace("checks['independent_paused_draft']=", "checks['native_palette_independent']=choices(draft)['graphics.sprites.animals.rhinos.palette'][3]==1\n        checks['independent_paused_draft']=")
s=s.replace('paths=[Path(__file__),reference]','paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
