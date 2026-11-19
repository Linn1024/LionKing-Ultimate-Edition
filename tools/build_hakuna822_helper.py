"""Prepare the complete reviewed later actor repertoire."""
from pathlib import Path
template=Path(__file__).with_name('build_hakuna814_helper.py')
s=template.read_text().replace('build/hakuna814-helper','build/hakuna822-helper')
exec(compile(s,str(template),'exec'))
