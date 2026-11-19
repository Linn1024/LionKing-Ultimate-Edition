"""Begin the short approach after the level-select loading macro releases control."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait461_rhino.py')
s=template.read_text().replace('build/cant-wait461-rhino','build/cant-wait462-rhino').replace("='1500'","='1800'").replace("'<1500H'","'<1800H'").replace('[0]*1250+[0x100]*55+[0]*195','[0]*1530+[0x100]*55+[0]*215')
s=s.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template,reference,')
exec(compile(s,str(template),'exec'))
