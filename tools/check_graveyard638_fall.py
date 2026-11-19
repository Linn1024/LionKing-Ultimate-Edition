"""Check ordinary fall death from the fresh direct-entry save, without forcing a death state."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard636_death.py')
s=template.read_text().replace('build/graveyard629-controls/stomp2/report.json','build/graveyard601-native-music/report.json').replace('build/graveyard636-death','build/graveyard638-fall')
s=s.replace("cmd=r['command'].copy()", "cmd=r['commands']['play'].copy()")
s=s.replace("i=cmd.index('--save-at');del cmd[i:i+3]", "if '--save-at' in cmd:\n    i=cmd.index('--save-at');del cmd[i:i+3]")
s=s.replace("('--frames','19800')", "('--frames','3000')").replace('18900,19200,19800','1800,2300,3000')
s=s.replace("for flag,value in (('--load'", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard619-helper/sprites.assets')\nfor flag,value in (('--load'")
s=s.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(s,str(template),'exec'))
