"""Enable already reviewed original drawings beyond the captured actor poses.

Use the existing ROM-pair catalog and bounded actor artwork banks. No nearest
pose substitutions or extra cartridge pixel assets are tracked.
"""
import json,re
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna821-repertoire';out.mkdir(exist_ok=True)
header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=header.read_text();a=text.index('\n{');b=text.index('\n};',a);rows={int(re.match(r'\{0x([0-9a-f]+),',line)[1],16):line for line in text[a+1:b].splitlines()};old=dict(rows)
file=ROOT/'tools/hakuna_destiny_actor_pairs.json';spec=json.loads(file.read_text());pairs={int(r['snes'],16):r for r in spec['pairs']};m=(ROOT/'Lion King, The (World).md').read_bytes();added=[]
banks=[(0x5a900,0x5c000,0x138cf4,0x13c184,14,7,3,6,[0xc58eb4,0xc58ea8]),(0x1e800,0x1f200,0x13cef4,0x13d99c,18,5,0,6,[0xc586d8]),(0x131a9,0x13480,0x10d934,0x10dca4,14,0,0,5,[0xc58ee4,0xc58ed8]),(0x3b1d5,0x3b300,0x10a22c,0x10a55c,14,0,3,5,[0xc58e9c]),(0x50500,0x50980,0x10ccdc,0x10d934,15,0,0,5,[0xc58afc,0xc58aec])]
for p,line in sorted(old.items()):
 if p in pairs or re.search(r'\}\},\d+,\d+,\d+,',line):continue
 q=int(re.match(r'\{0x[0-9a-f]+, 0x([0-9a-f]+),',line)[1],16)
 for lo,hi,ml,mh,role,nb,mb,level,owners in banks:
  if not (lo<=p<hi and ml<=q<mh):continue
  f=md_frame(m,q);assert f;x,y,w,h,_=bitmap(m,f,True,with_origin=True)
  row=dict(snes=hex(p),md=hex(q),role=role,native_palette=nb,md_palette=mb,native_to_md=list(range(16)),md_to_native=list(range(16)),basis='existing reviewed original indexed drawing/variant in the bounded actor artwork bank',owners=[dict(level=level,descriptor=hex(desc)) for desc in owners]);pairs[p]=row;added.append(row)
  rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{role},{nb},{mb}, {{'+','.join(map(str,range(16)))+'}, {'+','.join(map(str,range(16)))+'}},';break
spec['pairs']=[pairs[p] for p in sorted(pairs)];file.write_text(json.dumps(spec,indent=2)+'\n');header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:])
paths=[Path(__file__),file,header]
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',additional=len(added),total=len(pairs),pairs=added,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('Additional reviewed drawings',len(added),'total',len(pairs))
