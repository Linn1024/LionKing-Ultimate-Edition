"""Finish verified Exile rock effects and direct Stampede palette composition."""
from pathlib import Path
template=Path(__file__).with_name('build_next747.py')
s=template.read_text().replace('build/next743/build-report.json','build/next751/build-report.json').replace('build/next747\'', 'build/next754\'')
s=s.replace("('resources','wide','sprites')", "('resources','audio','wide')")
exec(compile(s,str(template),'exec'))
