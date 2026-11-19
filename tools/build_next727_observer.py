"""Private actual-owner inventory for Stampede and Exile, based on current720."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard697_observer.py')
s=template.read_text().replace('build/graveyard684/build-report.json','build/graveyard720/build-report.json').replace('build/graveyard697-observer','build/next727-observer')
s=s.replace('rd16(g_ram+0x1ff9e)==2 && rd24(g_ram+0xdf)==0xc003eb','(rd16(g_ram+0x1ff9e)==3 || rd16(g_ram+0x1ff9e)==4)')
exec(compile(s,str(template),'exec'))
