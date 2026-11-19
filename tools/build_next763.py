"""Finish observed Exile pickup ownership while preserving the qualified death/sound paths."""
from pathlib import Path
template=Path(__file__).with_name('build_next747.py')
s=template.read_text().replace('build/next743/build-report.json','build/next759/build-report.json').replace('build/next747\'', 'build/next763\'')
exec(compile(s,str(template),'exec'))
