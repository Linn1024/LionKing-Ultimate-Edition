"""Verify scripted hyena artwork/colors change in current fixed build and real Windows client."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard700_scripted_hyena.py')
s=template.read_text().replace('build/graveyard700-scripted-hyena','build/graveyard709-scripted').replace("ROOT/'dist/installed-preview684/LionKing.exe'", "ROOT/'build/graveyard708/player.exe'").replace('build/graveyard683-helper/sprites.assets','build/graveyard707-helper/sprites.assets')
s=s.replace('md_choices_leave_picture_native=','md_artwork_and_colors_visible=').replace("windows['snes']).getbbox() is None", "windows['snes']).getbbox() is not None")
s=s.replace("'GAP_CONFIRMED'", "'PASS'")
exec(compile(s,str(template),'exec'))
