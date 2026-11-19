"""Current executable pause/source/restart through real Windows resource tree."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_menu_audio80_ui.py')
source=original.read_text().replace("ROOT/'build/pride-menu-audio80'","ROOT/'build/pride-menu-enable86'")
exec(compile(source,str(original),'exec'))
