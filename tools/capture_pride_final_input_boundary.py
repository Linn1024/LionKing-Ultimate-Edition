"""Measure the first original Continue confirmation edge after the fade."""
from pathlib import Path

original=Path(__file__).with_name('capture_pride_final_input_reference.py')
source=original.read_text()
for before,after in [
    ("ROOT/'build/pride-final-input-reference'","ROOT/'build/pride-final-input-boundary'"),
    ("if name=='early-tap':", "if name.startswith('edge-'):return 256 if age==int(name.split('-')[1]) else 0\n    if name=='early-tap':"),
    ("('neutral','early-tap','early-release','held-through','after-fade')", "('edge-118','edge-120','edge-121','edge-122','edge-124')"),
    ('paths=[Path(__file__),source,','paths=[Path(__file__),original,source,')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
