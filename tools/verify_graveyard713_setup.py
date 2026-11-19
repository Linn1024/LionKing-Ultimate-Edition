"""Prepare the new Graveyard death sequence through actual Setup."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait464_setup.py')
s=template.read_text().replace('build/cant-wait459-helper/build-report.json','build/graveyard707-helper/build-report.json').replace('build/cant-wait460/build-report.json','build/graveyard708/build-report.json').replace('build/cant-wait464-setup','build/graveyard713-setup')
exec(compile(s,str(template),'exec'))
