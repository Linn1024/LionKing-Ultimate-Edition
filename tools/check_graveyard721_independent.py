"""The death-movement leaf alone must enable the native-width presentation path."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard711_death.py')
s=template.read_text().replace('build/graveyard711-death','build/graveyard721-independent').replace('build/graveyard708','build/graveyard720')
s=s.replace("(ROOT/'profiles/graveyard-md.ini').read_text()", "'schema = 1\\ngame = snes\\n'")
s=s.replace(",('retry',2600,'md',True)", "")
s=s.replace(",retry=cases['retry']['death']['selected']==0 and cases['retry']['gameplay']['health']>0", "")
exec(compile(s,str(template),'exec'))
