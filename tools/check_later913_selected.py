"""Complete the two levels with MD contacts selected as well as final art and sound."""
from pathlib import Path
template=Path(__file__).with_name('check_later902_selected.py');s=template.read_text().replace('build/later902-selected','build/later913-selected').replace('build/later901','build/later910').replace('build/later882-helper','build/later909-helper')
exec(compile(s,str(template),'exec'))
