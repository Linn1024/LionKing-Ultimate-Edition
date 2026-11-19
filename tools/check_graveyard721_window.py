"""Actual Windows death-only MD setting with native art, palette and viewport."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard712_death_window.py')
s=template.read_text().replace('build/graveyard712-death-window','build/graveyard721-window').replace('build/graveyard708','build/graveyard720').replace('build/graveyard711-death','build/graveyard721-independent')
exec(compile(s,str(template),'exec'))
