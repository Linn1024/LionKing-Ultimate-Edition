"""Repeat the focused hyena HUD trace with the corrected sprite latch."""
from pathlib import Path
template357=Path(__file__).with_name('probe_hyena_hud354.py')
source=template357.read_text().replace("base=ROOT/'build/level-caption349'","base=ROOT/'build/hyena-hud356'")
source=source.replace('hyena-hud354','hyena-hud357')
source=source.replace('Path(__file__),bp,','Path(__file__),template357,bp,')
exec(compile(source,str(template357),'exec'))
