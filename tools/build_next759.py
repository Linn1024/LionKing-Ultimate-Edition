"""Final next-level sound availability and truthful resource help."""
from pathlib import Path
template=Path(__file__).with_name('build_next747.py')
s=template.read_text().replace('build/next743/build-report.json','build/next754/build-report.json').replace('build/next747\'', 'build/next759\'')
s=s.replace("('resources','wide','sprites')", "('resources','audio')")
exec(compile(s,str(template),'exec'))
