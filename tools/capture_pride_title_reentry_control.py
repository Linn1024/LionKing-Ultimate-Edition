"""Capture the native-caption control for the actual current owned revive route."""
from pathlib import Path

template=Path(__file__).with_name('capture_pride_title_reentry.py')
source=template.read_text()
changes={
    "ROOT/'build/pride-title-reentry'":"ROOT/'build/pride-title-reentry-control'",
    "'\\ngraphics.titles.pride_lands = md\\n'":"'\\ngraphics.titles.pride_lands = snes\\n'",
    'paths=[Path(__file__),binary,':'paths=[Path(__file__),template,binary,',
    "sorted(report['artifacts_sha256'])":"len(report['artifacts_sha256'])",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(template),'exec'))
