"""Compare actual owned Stampede/Exile frames, keeping unmatched poses explicit."""
import csv,json,collections,hashlib,re,struct
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
out=ROOT/'build/next731-sprites';out.mkdir(exist_ok=True)
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes()
md_hydrated={}
for level,field in ((3,21000),(4,24500)):
 work=bytearray(m);work.extend(bytes(0x1000000-len(work)));work[0xff0000:]=(ROOT/f'build/next726-reference/{field}-68K RAM.bin').read_bytes();md_hydrated[level]=work
native=list(csv.DictReader((ROOT/'build/next729-route/poses.csv').open()));external=list(csv.DictReader((ROOT/'build/next726-reference/poses.csv').open()))
families=[('stampede-cub','c5858a','07d728'),('wildebeest1','c58b0c','1b5b18'),('wildebeest2','c58b18','1b5b26'),('wildebeest3','c58b24','1b5b34'),('wildebeest4','c58b30','1b5b42'),('rocks','c58b3c','1b5b50'),('exile-lizard','c58c50','09793a'),('exile-chameleon','c58ca4','09798e'),('exile-running-lizard','c58c5c','097948')]
hydrated={}
for level in (3,4):
 folder=ROOT/f'build/next725-baseline/{level}-md';raw=(folder/'entry.state').read_bytes();expected=re.findall(r'wram_sha256=([a-f0-9]+)',(folder/'run.log').read_text())[-1]
 scene=json.loads((folder/'scene.json').read_text());needle=(0xc00000|scene['latched_gameplay']['descriptor']).to_bytes(3,'little');offsets=[];start=0
 while (at:=raw.find(needle,start))>=0:
  start=at+1;offset=at-0xdf
  if offset>=0 and hashlib.sha256(raw[offset:offset+0x20000]).hexdigest()==expected:offsets.append(offset)
 assert len(offsets)==1,(level,offsets)
 work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3e0000:]=raw[offsets[0]:offsets[0]+0x20000];hydrated[level]=work
def image(rom,pose,md):
 p=int(pose,16)&(0xffffff if md else 0x3fffff);f=(md_frame if md else snes_frame)(rom,p)
 if not f:return None
 b=bitmap(rom,f,md,with_origin=True);return b if len(b)==5 else None
def norm(b):
 if not b:return None
 colors={0:0};data=[]
 for c in b[4]:
  if c not in colors:colors[c]=len(colors)
  data.append(colors[c])
 return (b[2],b[3],bytes(data))
rows=[]
for name,nd,md in families:
 level=4 if name.startswith('exile') else 3
 ns={r['pose']:r for r in native if r['descriptor']==nd};ms={r['pose']:r for r in external if r['descriptor']==md and int(r['level'])==level};nb={p:image(hydrated[level],p,False) for p in ns};mb={p:image(md_hydrated[level],p,True) for p in ms};pairs=[];missing=[]
 for p,b in nb.items():
  matches=[q for q,c in mb.items() if b and c and norm(b)==norm(c)]
  if matches:pairs.append(dict(snes=p,md=matches,origin=b[:2],md_origin=mb[matches[0]][:2],size=b[2:4]))
  else:missing.append(dict(pose=p,decoded=b is not None,size=b[2:4] if b else None))
 masks=[]
 for p,b in nb.items():
  matches=[q for q,c in mb.items() if b and c and b[2:4]==c[2:4] and bytes(bool(v) for v in b[4])==bytes(bool(v) for v in c[4])]
  if matches:masks.append(dict(snes=p,md=matches,origin=b[:2],md_origin=mb[matches[0]][:2],size=b[2:4]))
 row=dict(family=name,native_descriptor=nd,md_descriptor=md,native=len(ns),external=len(ms),exact_pairs=pairs,silhouette_pairs=masks,unmatched=missing)
 rows.append(row);print(name,len(ns),len(ms),'exact',len(pairs),'silhouettes',len(masks),'missing',len(missing),missing[:3])
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',families=rows),indent=2)+'\n')
