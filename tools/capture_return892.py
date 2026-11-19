"""Actual Windows full mixed Return scenery and adult actor client."""
from pathlib import Path
template=Path(__file__).with_name('capture_later886_actors.py');s=template.read_text().replace('build/later886-windows','build/return892-windows').replace('[(7,44500,44560),(8,52000,52100)]','[(8,52000,52100)]').replace('build/later883/build-report.json','build/return889/build-report.json')
s=s.replace("cmd.remove('--no-pace')", "cmd[0]=str(ROOT/'build/return889/player.exe');cmd.remove('--no-pace')").replace('if level==7 else','if level==8 else')
exec(compile(s,str(template),'exec'))
