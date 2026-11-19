"""Walk into the nearby hyena, then release controls through ordinary death and retry."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard636_death.py')
s=template.read_text().replace('build/graveyard636-death','build/graveyard637-death')
s=s.replace("(out/'idle.polled.tape').write_bytes(bytes(4000))", "(out/'idle.polled.tape').write_bytes(bytes((0,1))*100+bytes(3800))")
s=s.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(s,str(template),'exec'))
