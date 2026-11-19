"""HUD isolation in settled gameplay, after the opening caption."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride419_hud.py')
s=template.read_text().replace('build/pride419-hud','build/pride421-hud-play').replace("'1500'","'2200'")
s=s.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(s,str(template),'exec'))
