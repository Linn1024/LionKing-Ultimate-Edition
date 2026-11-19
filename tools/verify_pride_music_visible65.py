"""Repeat source restarts with OS captures after the level's startup fade."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_music_ui65.py')
source=original.read_text().replace("base/'windows-ui'", "base/'windows-visible'")
anchor="r['field']>=1200 and r['descriptor']==0xc00387"
assert source.count(anchor)==1
source=source.replace(anchor,"r['field']>=2200 and r['descriptor']==0xc00387")
source=source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
