"""Map the native opaque Stampede matte to its original MD black palette slot."""
from pathlib import Path
template=Path(__file__).with_name('build_next747.py')
s=template.read_text().replace('build/next743/build-report.json','build/next766/build-report.json').replace('build/next747\'', 'build/next771\'')
s=s.replace("('resources','wide','sprites')", "('wide',)")
exec(compile(s,str(template),'exec'))
