"""Measure actual destination readiness with the reviewed ROM-backed fast load."""
from pathlib import Path

original=Path(__file__).with_name('capture_pride_late_visible.py')
source=original.read_text()
for before,after in [
    ("ROOT/'build/pride-late-visible'","ROOT/'build/pride-final-fast-assets-probe/capture'"),
    ("ROOT/'build/pride-bounce-owner-work/player/final-skip-late-probe'","ROOT/'build/pride-final-fast-assets-probe'"),
    ("TLK_FINAL_LATE_SKIP='1'","TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1'"),
    ('paths=[Path(__file__),probe/', 'paths=[Path(__file__),original,probe/')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
