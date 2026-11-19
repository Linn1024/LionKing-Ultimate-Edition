"""Use the normal Tab toggle to close the root settings menu after live Apply."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride422_hud_ui.py')
s=template.read_text().replace('build/pride422-hud-ui','build/pride423-hud-ui').replace('key(0x1b);key(0x1b);key(0x1b)','key(0x1b);key(0x1b);key(0x09)')
exec(compile(s,str(template),'exec'))
