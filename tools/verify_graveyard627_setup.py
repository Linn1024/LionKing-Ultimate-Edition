"""Actual isolated native Setup for four added vulture collision records."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait464_setup.py')
s=template.read_text().replace('build/cant-wait459-helper/build-report.json','build/graveyard619-helper/build-report.json').replace('build/cant-wait460/build-report.json','build/graveyard621/build-report.json').replace('build/cant-wait464-setup','build/graveyard627-setup')
exec(compile(s,str(template),'exec'))
