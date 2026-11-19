"""Resolve original Continue confirmation between the known122/124 boundaries."""
from pathlib import Path

original=Path(__file__).with_name('capture_pride_final_input_reference.py')
source=original.read_text()
for before,after in [
    ("ROOT/'build/pride-final-input-reference'","ROOT/'build/pride-final-input-first-edge'"),
    ("if name=='early-tap':", "if name=='edge-123':return 256 if age==123 else 0\n    if name=='early-tap':"),
    ("('neutral','early-tap','early-release','held-through','after-fade')", "('edge-123',)"),
    ('paths=[Path(__file__),source,','paths=[Path(__file__),original,source,')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
