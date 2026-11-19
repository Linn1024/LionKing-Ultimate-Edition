"""Tail palette live UI, using the corrected retained bank1 image qualification."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait475_ui.py')
s=template.read_text().replace('build/cant-wait474-tail/report.json','build/cant-wait477-tail-qualified/report.json').replace('build/cant-wait475-ui','build/cant-wait480-ui')
exec(compile(s,str(template),'exec'))
