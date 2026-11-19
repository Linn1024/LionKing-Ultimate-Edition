"""Prepare owned Scar/fire artwork by original bitmap correspondence; preserve earlier images."""
import collections,csv,json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride925-actors';out.mkdir(exist_ok=True);s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();r=json.loads((ROOT/'build/pride922-actors/report.json').read_text());pairs={};extra={}
native=bytearray(s);native.extend(bytes(0x400000-len(native)));state=(ROOT/'build/later904-fallback/pride-rock.native.state').read_bytes();at=state.find(bytes.fromhex('4905c0'))-0xdf;assert at>=0 and state[at+0x1ff9e:at+0x1ffa0]==b'\x09\0';native[0x3e0000:]=state[at:at+0x20000]

def crop(b):
 x,y,w,h,p=b;pts=[(i%w,i//w) for i,c in enumerate(p) if c];left=min(x for x,y in pts);right=max(x for x,y in pts)+1;top=min(y for x,y in pts);bottom=max(y for x,y in pts)+1;return right-left,bottom-top,bytes(p[y*w+x] for y in range(top,bottom) for x in range(left,right))
def shape(b):
 w,h,p=crop(b);c={0:0};out=[]
 for v in p:
  if v not in c:c[v]=len(c)
  out.append(c[v])
 return w,h,bytes(out)
# Original Scar animation operands, including poses absent from the sampled movie.
for a in range(0x156928,0x157500):
 if not 0<m[a]<128:continue
 p=int.from_bytes(m[a+1:a+4],'big')
 if not 0x17a400<=p<0x17f000:continue
 f=md_frame(m,p)
 if f:
  try:b=bitmap(m,f,True,with_origin=True);extra[p]=b
  except (IndexError,ValueError):pass
index=collections.defaultdict(list)
for p,b in extra.items():index[shape(b)].append(p)
def mdcolor(v):
 c=[((v>>sh)&7)*4+(((v>>sh)&7)>>2) for sh in (1,5,9)];return c[0]|c[1]<<5|c[2]<<10
def dist(a,b):return sum(w*(((a>>sh)&31)-((b>>sh)&31))**2 for sh,w in [(0,3),(5,6),(10,2)])
for f in r['families']:
 desc=f['native_descriptor'];scar=desc in ['c585e8','c585f4','c58600'];fire=desc in ['c5866c','c58678','c58618','c5863c','c58624','c58630']
 if not(scar or fire):continue
 candidates={int(p['snes'],16)&0x3fffff:[int(q,16) for q in p['md']] for p in f['pairs']}
 if scar:
  for missing in f['missing']:
   p=int(missing['pose'],16)&0x3fffff;b=bitmap(native,snes_frame(native,p),False,with_origin=True);qs=index.get(shape(b),[])
   if qs:candidates[p]=qs
 for p,qs in candidates.items():
  b=bitmap(native,snes_frame(native,p),False,with_origin=True);q=min(qs,key=lambda q:sum(abs(x-y) for x,y in zip(b[:2],bitmap(m,md_frame(m,q),True,with_origin=True)[:2])));z=bitmap(m,md_frame(m,q),True,with_origin=True);a=crop(b);t=crop(z);assert a[:2]==t[:2] and bytes(map(bool,a[2]))==bytes(map(bool,t[2]))
  nb=7 if scar else 4;np=0x7d73 if scar else 0x7d13;ca=struct.unpack_from('<16H',s,np);cb=[mdcolor(v) for v in struct.unpack_from('>16H',m,0x8e638+96)];v=collections.defaultdict(collections.Counter)
  for x,y in zip(a[2],t[2]):
   if x and y:v[x][y]+=1
  nm=[0]+[v[i].most_common(1)[0][0] if v[i] else min(range(1,16),key=lambda j:dist(ca[i],cb[j])) for i in range(1,16)];mn=[0]+[min(range(1,16),key=lambda j:dist(cb[i],ca[j])) for i in range(1,16)]
  row=dict(snes=hex(p),md=hex(q),role=20 if scar else 15,native_palette=nb,md_palette=3,native_to_md=nm,md_to_native=mn,basis='owned native Scar/fire image and original MD occupied pixel/index correspondence',owners=[dict(level=9,descriptor='0x'+desc)])
  if p in pairs:
   assert all(pairs[p][k]==row[k] for k in ['md','role','native_palette','native_to_md','md_to_native']),(hex(p),pairs[p]['md'],row['md']);pairs[p]['owners']+=row['owners']
  else:pairs[p]=row
file=ROOT/'tools/pride_actor_pairs.json';file.write_text(json.dumps(dict(scope=__doc__,pairs=[pairs[p] for p in sorted(pairs)]),indent=2)+'\n');header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=header.read_text();a=text.index('\n{');b=text.index('\n};',a);rows={int(re.match(r'\{0x([0-9a-f]+),',l)[1],16):l for l in text[a+1:b].splitlines()};old=len(rows)
for p,row in pairs.items():
 if p in rows:assert int(re.match(r'\{0x[0-9a-f]+, 0x([0-9a-f]+),',rows[p])[1],16)==int(row['md'],16),hex(p)
 q=int(row['md'],16);x,y,w,h,_=bitmap(m,md_frame(m,q),True,with_origin=True);rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{row["role"]},{row["native_palette"]},{row["md_palette"]}, {{'+','.join(map(str,row['md_to_native']))+'}, {'+','.join(map(str,row['native_to_md']))+'}},'
header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:]);paths=[Path(__file__),file,ROOT/'build/pride922-actors/report.json',header];(out/'report.json').write_text(json.dumps(dict(result='PREPARED',links=len(pairs),scar_links=sum(p['role']==20 for p in pairs.values()),images=len(rows),old_images=old,original_scar_operands=len(extra),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('Prepared',len(pairs),'links',len(rows),'images',sum(p['role']==20 for p in pairs.values()),'Scar',flush=True)
