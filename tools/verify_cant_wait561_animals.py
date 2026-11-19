"""Repeat only the connected failed animal segment after actual sound-owner correction."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait556_animals.py')
s=template.read_text().replace('build/cant-wait555/build-report.json','build/cant-wait560/build-report.json').replace('build/cant-wait556-animals','build/cant-wait561-animals')
s=s.replace('paths=[Path(__file__),reference,', "paths=[Path(__file__),template,ROOT/'build/cant-wait558-owner-qualified/report.json',reference,")
exec(compile(s,str(template),'exec'))
