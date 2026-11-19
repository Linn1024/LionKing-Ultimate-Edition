"""Prepare the MD death sequence with unchanged artwork and prior gameplay data."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard683_helper.py')
s=template.read_text().replace('build/graveyard683-helper','build/graveyard707-helper')
exec(compile(s,str(template),'exec'))
