"""Inspect the installed Graveyard client with inherited level/death choices and preserved gameplay choices."""
from pathlib import Path
template=Path(__file__).with_name('verify_graveyard632_installed.py')
s=template.read_text().replace('build/graveyard631-publication/report.json','build/graveyard646-publication/report.json').replace('build/graveyard632-installed','build/graveyard647-installed').replace("'sprite_assets=loaded'", "'resource_cache=loaded'")
s=s.replace("paths=[Path(__file__),publication", "checks['music_children_inherit_md']=all(choices['audio.music.elephant_graveyard.'+name][4]==2 for name in ('track','death'))\npaths=[Path(__file__),template,publication")
exec(compile(s,str(template),'exec'))
