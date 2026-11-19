"""Retain last-life fade/control presentation with the input-refresh controller."""
from pathlib import Path

original=Path(__file__).with_name('capture_pride_final_scene.py')
source=original.read_text()
for before,after in [
    ('build/pride-final-scene-probe3','build/pride-final-input-refresh-probe2'),
    ('paths=[Path(__file__),base/', 'paths=[Path(__file__),original,base/')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
