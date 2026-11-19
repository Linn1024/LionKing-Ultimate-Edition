"""Build the scene controller with original input servicing during its hold."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_final_input_probe.py')
source=original.read_text()
for before,after in [
    ('build/pride-final-input-probe2','build/pride-final-input-refresh-probe2'),
    ('tools/pride_final_input_probe.c','tools/pride_final_input_refresh_probe.c'),
    ('ROOT/"tools/build_pride_final_scene_probe.py",','ROOT/"tools/build_pride_final_scene_probe.py",ROOT/"tools/build_pride_final_input_probe.py",')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
