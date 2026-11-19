"""Build shared level-two HUD after validating visible colors (OBJ index0 is transparent)."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait479.py')
s=template.read_text().replace("out=ROOT/'build/cant-wait479'","out=ROOT/'build/cant-wait482'")
exec(compile(s,str(template),'exec'))
