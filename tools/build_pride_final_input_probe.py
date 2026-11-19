"""Build the isolated final-scene input/Continue controller from the pinned graph."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_final_scene_probe.py')
source=original.read_text()
for before,after in [
    ('build/pride-final-scene-probe3','build/pride-final-input-probe2'),
    ('tools/pride_final_scene_probe.c','tools/pride_final_input_probe.c'),
    ('paths=[Path(__file__),original,fast_original,', 'paths=[Path(__file__),original,ROOT/"tools/build_pride_final_scene_probe.py",ROOT/"tools/pride_final_scene_probe.c",fast_original,')]:
    assert source.count(before)>=1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
