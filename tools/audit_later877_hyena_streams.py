"""Review full original adult-hyena frame operands, including unobserved program poses."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame
from build_pride_compiled_hooks import digest
out=ROOT/'build/later877-hyena-streams';out.mkdir(exist_ok=True);groups={}
for name,romname,lo,hi,plo,phi,md in [('snes','Lion King, The (USA).sfc',0x24ddc,0x2519b,0xc61c00,0xc63400,False),('md','Lion King, The (World).md',0x140000,0x140380,0x15363a,0x1563ea,True)]:
 rom=(ROOT/romname).read_bytes();tokens={}
 for p in range(lo,hi-3):
  if not 0<rom[p]<128:continue
  pose=int.from_bytes(rom[p+1:p+4],'big' if md else 'little')
  if not plo<=pose<phi:continue
  if (md_frame if md else snes_frame)(rom,pose if md else pose&0x3fffff):tokens[p]=(rom[p],pose)
 result=[]
 for p in sorted(q for q in tokens if q-4 not in tokens):
  seq=[];q=p
  while q in tokens:duration,pose=tokens[q];seq.append(dict(duration=duration,pose=hex(pose)));q+=4
  result.append(dict(address=hex(p),end=hex(q),frames=seq))
 groups[name]=result
 for r in result:print(name,r['address'],' '.join(f"{x['pose']}:{x['duration']}" for x in r['frames']),flush=True)
paths=[Path(__file__),ROOT/'build/later875-actors/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',groups=groups,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
