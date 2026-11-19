"""Current candidate pending-reaction continuation after all audio leaves were added."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait562_pending_save.py')
s=template.read_text().replace('build/cant-wait561-animals/report.json','build/cant-wait574-native-control/report.json').replace('build/cant-wait562-pending-save','build/cant-wait575-current-save')
exec(compile(s,str(template),'exec'))
