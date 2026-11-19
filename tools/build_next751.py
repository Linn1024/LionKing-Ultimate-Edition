"""Cache Stampede choices per scanline and resolve shared actors once per piece."""
from pathlib import Path
template=Path(__file__).with_name('build_next747.py')
s=template.read_text().replace('build/next743/build-report.json','build/next747/build-report.json').replace('build/next747\'', 'build/next751\'')
s=s.replace("('resources','wide','sprites')", "('wide',)")
exec(compile(s,str(template),'exec'))
