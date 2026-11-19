"""Capture both valid eight-color death clients in a fresh recording folder."""
from pathlib import Path
template=Path(__file__).with_name('capture_hakuna852_death.py')
s=template.read_text().replace('build/hakuna852-death','build/hakuna854-death')
exec(compile(s,str(template),'exec'))
