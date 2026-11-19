"""Private actor inventory for the next two scenes, with no maintained runtime edit."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard697_observer.py')
s=template.read_text().replace('build/graveyard684/build-report.json','build/next771/build-report.json').replace('build/graveyard697-observer','build/hakuna779-observer')
s=s.replace('rd16(g_ram+0x1ff9e)==2 && rd24(g_ram+0xdf)==0xc003eb','(rd16(g_ram+0x1ff9e)==5 || rd16(g_ram+0x1ff9e)==6)')
exec(compile(s,str(template),'exec'))
