"""Inspect the installed all-MD CMD after the native/MD music ownership correction."""
from pathlib import Path
template=Path(__file__).with_name('verify_graveyard655_cmd.py')
s=template.read_text().replace('build/graveyard654-publication/report.json','build/graveyard670-publication/report.json').replace('build/graveyard655-cmd','build/graveyard671-installed')
s=s.replace('paths=[Path(__file__),publication,','paths=[Path(__file__),template,publication,')
exec(compile(s,str(template),'exec'))
