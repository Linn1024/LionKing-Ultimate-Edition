"""Actual source tree and restarts on the output-only menu candidate."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_menu_audio80_ui.py')
source=original.read_text().replace("ROOT/'build/pride-menu-audio80'","ROOT/'build/pride-menu-output83'")
exec(compile(source,str(original),'exec'))
