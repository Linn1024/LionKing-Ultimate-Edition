"""Bounded controls for gameplay changes, including prepared asset preservation."""
from pathlib import Path
template=Path(__file__).with_name('verify_graveyard605_native_seams.py')
s=template.read_text().replace('build/graveyard599/build-report.json','build/graveyard621/build-report.json').replace('build/graveyard605-native-seams','build/graveyard622-native').replace("ROOT/'build/cant-wait579/player.exe'","ROOT/'build/graveyard609/player.exe'")
s=s.replace("(folder/'host.ini').write_text", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/('build/graveyard529-helper/sprites.assets' if name=='old' else 'build/graveyard619-helper/sprites.assets'))\n        (folder/'host.ini').write_text")
exec(compile(s,str(template),'exec'))
