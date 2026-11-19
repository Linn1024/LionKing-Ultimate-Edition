"""Build level-two shared HUD artwork, retaining the independent tail palette."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait473.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait460'","base=ROOT/'build/cant-wait473'").replace("out=ROOT/'build/cant-wait473'","out=ROOT/'build/cant-wait479'")
exec(compile(s,str(template),'exec'))
