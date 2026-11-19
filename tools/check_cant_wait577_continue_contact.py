"""Inspect only the known Continue contact from the same short ride checkpoint."""
from pathlib import Path
template=Path(__file__).with_name('check_cant_wait576_continue.py')
s=template.read_text().replace('build/cant-wait576-continue','build/cant-wait577-continue-contact').replace("'4100'","'4102'")
exec(compile(s,str(template),'exec'))
