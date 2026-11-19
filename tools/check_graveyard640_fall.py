"""Wait on the low bone-platform checkpoint to exercise a real fall death."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard636_death.py')
s=template.read_text().replace('build/graveyard629-controls/stomp2/report.json','build/graveyard592-native-owners/report.json').replace('build/graveyard636-death','build/graveyard640-fall')
s=s.replace("cmd=r['command'].copy()", "cmd=r['cases'][0]['command'].copy()")
s=s.replace("str(reference.parent/'entry.state')", "str(reference.parent/'14248/entry.state')")
s=s.replace("('--frames','19800')", "('--frames','15500')").replace('18900,19200,19800','14700,15100,15500')
s=s.replace("for flag,value in (('--load'", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard619-helper/sprites.assets')\nfor flag,value in (('--load'")
s=s.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(s,str(template),'exec'))
