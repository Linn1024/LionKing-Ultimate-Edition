"""Short final native-control and first-animal check after connecting the common parser."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait556_animals.py')
s=template.read_text().replace('build/cant-wait555/build-report.json','build/cant-wait572/build-report.json').replace('build/cant-wait556-animals','build/cant-wait574-native-control')
s=s.replace(",('rhino',build.parent/'player.exe',('rhino',)),('reaction',build.parent/'player.exe',('reaction',))",'')
a=s.index(',rhino_independent=');b=s.index(',gameplay_picture_preserved=',a);s=s[:a]+s[b:]
exec(compile(s,str(template),'exec'))
