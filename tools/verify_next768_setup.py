"""Check actual Setup imports the enlarged sprite package and both scene palettes."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait464_setup.py')
s=template.read_text().replace('build/cant-wait459-helper/build-report.json','build/next741-helper/build-report.json').replace('build/cant-wait460/build-report.json','build/next766/build-report.json').replace('build/cant-wait464-setup','build/next768-setup')
exec(compile(s,str(template),'exec'))
