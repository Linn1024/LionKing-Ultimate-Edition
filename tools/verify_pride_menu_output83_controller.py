"""Menu dispatch preserves native CPU calls; source/tail/current-history guards."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_menu_audio80_component.py')
source=original.read_text().replace("ROOT/'build/pride-menu-audio80-component'","ROOT/'build/pride-menu-output83-controller'")
source=source.replace('paths+=[Path(__file__),','paths+=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
