"""Focused Return background/color choices, native control and current save."""
from pathlib import Path
template=Path(__file__).with_name('check_be_prepared868_choices.py');s=template.read_text().replace('build/be-prepared868-choices','build/return891-choices').replace('build/be-prepared866/build-report.json','build/return889/build-report.json').replace('build/be-prepared866/player.exe','build/return889/player.exe').replace('dist/installed-preview849/LionKing.exe','build/later883/player.exe')
s=s.replace('build/destiny863-handoff/be-prepared.native.state','build/later872-route/later.native.state').replace('build/destiny863-handoff/after44500.polled.tape','build/later872-route/after52000.polled.tape').replace('44740','52240').replace('44620','52120').replace("v['level']==7", "v['level']==8")
s=s.replace("if name=='restored':", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/later882-helper/sprites.assets')\n if name=='restored':")
exec(compile(s,str(template),'exec'))
