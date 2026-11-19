"""Read-only scene/owner/pose/palette inventory for the remaining main and bonus stages."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard697_observer.py');s=template.read_text()
s=s.replace('build/graveyard684/build-report.json','build/be-prepared866/build-report.json').replace('build/graveyard697-observer','build/later871-observer')
s=s.replace('rd16(g_ram+0x1ff9e)==2 && rd24(g_ram+0xdf)==0xc003eb','rd16(g_ram+0x1ff9e)>=7 && rd16(g_ram+0x1ff9e)<=13')
s=s.replace('palette,descriptor,action,actor_x,actor_y,mapped_role,colors','palette,descriptor,action,actor_x,actor_y,mapped_role,level,colors')
s=s.replace('((uint64_t)descriptor<<32)|piece->pose|palette<<24','((uint64_t)rd16(g_ram+0x1ff9e)<<56)|((uint64_t)descriptor<<32)|piece->pose|palette<<24')
s=s.replace('descriptor,actor?rd24', 'descriptor,actor?rd24')
s=s.replace('fprintf(pose_trace,"%06x,%06x,%u,%u,%u,",', 'fprintf(pose_trace,"%06x,%06x,%u,%u,%u,%u,",')
s=s.replace('TlkMdSpritesDrawRole(piece->pose,palette));', 'TlkMdSpritesDrawRole(piece->pose,palette),rd16(g_ram+0x1ff9e));')
exec(compile(s,str(template),'exec'))
