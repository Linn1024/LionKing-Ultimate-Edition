"""Build the excluded ROM-derived final-destination asset experiment."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_final_display_probe.py')
source=original.read_text()
for before,after in [
    ("ROOT/'build/pride-final-display-probe2'","ROOT/'build/pride-final-fast-assets-probe'"),
    ('tools/pride_final_display_probe.c','tools/pride_final_fast_assets_probe.c'),
    ('paths=[Path(__file__),source,','paths=[Path(__file__),original,source,')]:
    assert source.count(before)>=1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
