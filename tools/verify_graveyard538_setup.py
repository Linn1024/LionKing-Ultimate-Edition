"""Actual isolated installation of prepared vulture sprites/native palette5, other assets retained."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait464_setup.py')
s=template.read_text().replace('build/cant-wait459-helper/build-report.json','build/graveyard529-helper/build-report.json').replace('build/cant-wait460/build-report.json','build/graveyard536/build-report.json').replace('build/cant-wait464-setup','build/graveyard538-setup')
exec(compile(s,str(template),'exec'))
