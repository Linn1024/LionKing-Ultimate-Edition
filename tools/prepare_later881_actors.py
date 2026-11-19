"""Freeze original adult-hyena action pairs and reviewed static Be Prepared objects."""
import collections,json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/later881-actors';out.mkdir(exist_ok=True);s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();report=json.loads((ROOT/'build/later877-hyena-streams/report.json').read_text());ns={int(r['address'],16):r['frames'] for r in report['groups']['snes']};ms={int(r['address'],16):r['frames'] for r in report['groups']['md']};links={};conflicts=set();pairs={}
def add(a,b,basis):
 assert len(a)==len(b)
 for n,z in zip(a,b):
  assert n['duration']==z['duration'];p=int(n['pose'],16)&0x3fffff;q=int(z['pose'],16)
  if p in links and links[p][0]!=q:conflicts.add(p)
  links[p]=(q,basis)
for a,b in [(0x24ddc,0x140044),(0x24e36,0x14008a),(0x24e58,0x1400ac),(0x24e90,0x1400e8),(0x24ea2,0x1400fa),(0x24eaa,0x140102),(0x24eb4,0x14010c),(0x24eba,0x140112),(0x24ec4,0x14011c),(0x24f50,0x140172),(0x2509b,0x1402b6)]:add(ns[a],ms[b],f'corresponding original action phases {a:06x}/{b:06x}')
add(ns[0x24e08],ms[0x140070]+ms[0x140076],'original idle loop; MD event2 follows first pose, native event2 separates loops')
add(ns[0x25045]+ns[0x25053]+ns[0x25079],ms[0x140264],'original attack phases, including native split marker groups')
def mdcolor(c):
 v=[((c>>sh)&7)*4+(((c>>sh)&7)>>2) for sh in (1,5,9)];return v[0]|v[1]<<5|v[2]<<10
def distance(a,b):return sum(w*(((a>>sh)&31)-((b>>sh)&31))**2 for sh,w in ((0,3),(5,6),(10,2)))
def colors(nb,mb):
 ca=list(struct.unpack_from('<16H',s,nb));cb=[mdcolor(v) for v in struct.unpack_from('>16H',m,0x24ef66+mb*32)];return ca,cb
def nearest(a,b):return [0]+[min(range(1,16),key=lambda j:distance(a[i],b[j])) for i in range(1,16)]
ca,cb=colors(0x7d53,3)
for p,(q,basis) in links.items():
 if p in conflicts:continue
 pairs[p]=dict(snes=hex(p),md=hex(q),role=19,native_palette=6,md_palette=3,native_to_md=nearest(ca,cb),md_to_native=nearest(cb,ca),basis=basis,owners=[dict(level=level,descriptor='0xc58ecc') for level in (7,8)])
# Shared static artwork with cropped pixel/opacity correspondence. Dynamic RAM
# columns and unreviewed variants deliberately stay native.
native=bytearray(s);native.extend(bytes(0x400000-len(native)));data=(ROOT/'build/destiny863-handoff/be-prepared.native.state').read_bytes();needle=bytes.fromhex('e504c0');at=data.find(needle)-0xdf;assert at>=0 and data[at+0x1ff9e:at+0x1ffa0]==b'\x07\0';native[0x3e0000:]=data[at:at+0x20000]
families=json.loads((ROOT/'build/later875-actors/report.json').read_text())['families'];header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=header.read_text();a=text.index('\n{');b=text.index('\n};',a);old={int(re.match(r'\{0x([0-9a-f]+),',l)[1],16):l for l in text[a+1:b].splitlines()};rows=dict(old)
def crop(b):
 x,y,w,h,pix=b;pts=[(i%w,i//w) for i,c in enumerate(pix) if c];left=min(x for x,y in pts);right=max(x for x,y in pts)+1;top=min(y for x,y in pts);bottom=max(y for x,y in pts)+1;return right-left,bottom-top,bytes(pix[y*w+x] for y in range(top,bottom) for x in range(left,right))
def mapping(a,b,ca,cb):
 a=crop(a);b=crop(b);assert a[:2]==b[:2] and bytes(bool(c) for c in a[2])==bytes(bool(c) for c in b[2]);v=collections.defaultdict(collections.Counter)
 for x,y in zip(a[2],b[2]):
  if x and y:v[x][y]+=1
 return [0]+[v[c].most_common(1)[0][0] if v[c] else min(range(1,16),key=lambda n:distance(ca[c],cb[n])) for c in range(1,16)]
for desc,mdesc,role,bank,mb,palette in [('c587d6','112312',14,0,0,0x7c93),('c58780','13fe04',15,2,2,0x2f7c7),('c5878c','13fe64',15,5,2,0x2f927),('c5873a','13fee2',15,2,2,0x2f7c7),('c58758','13fee2',15,2,2,0x2f7c7),('c5870a','13fe94',15,2,2,0x2f7c7),('c5872a','13fec8',15,2,2,0x2f7c7)]:
 f=next(r for r in families if r['level']==7 and r['native_descriptor']==desc);ca,cb=colors(palette,mb)
 for pair in f['pairs']:
  p=int(pair['snes'],16)&0x3fffff
  if pair['native_palette']!=bank or mdesc not in pair['owners']:continue
  qs=[int(q,16) for q in pair['md']];oldq=int(re.match(r'\{0x[0-9a-f]+, 0x([0-9a-f]+),',old[p])[1],16) if p in old else None;q=oldq if oldq in qs else qs[0]
  n=bitmap(native,snes_frame(native,p),False,with_origin=True);z=bitmap(m,md_frame(m,q),True,with_origin=True)
  row=dict(snes=hex(p),md=hex(q),role=role,native_palette=bank,md_palette=mb,native_to_md=mapping(n,z,ca,cb),md_to_native=mapping(z,n,cb,ca),basis='actual owned static image, occupied pixel/opacity correspondence',owners=[dict(level=7,descriptor='0x'+desc)])
  if p in pairs:assert all(pairs[p][k]==row[k] for k in ('md','role','native_palette','md_palette','native_to_md','md_to_native'));pairs[p]['owners']+=row['owners']
  else:pairs[p]=row
for p,row in pairs.items():
 q=int(row['md'],16);x,y,w,h,_=bitmap(m,md_frame(m,q),True,with_origin=True);rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{row["role"]},{row["native_palette"]},{row["md_palette"]}, {{'+','.join(map(str,row['md_to_native']))+'}, {'+','.join(map(str,row['native_to_md']))+'}},'
file=ROOT/'tools/later_actor_pairs.json';file.write_text(json.dumps(dict(scope='Reviewed adult-hyena original phase drawings and static Be Prepared objects. Native timings/AI and unknown/action-ambiguous art remain.',pairs=[pairs[p] for p in sorted(pairs)],unmapped_ambiguous_native=[hex(p) for p in sorted(conflicts)]),indent=2)+'\n');header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:])
paths=[Path(__file__),file,header,ROOT/'tools/later_sprite_catalog.py',ROOT/'build/later877-hyena-streams/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',old_images=len(old),new_images=len(rows),links=len(pairs),hyena_links=sum(r['role']==19 for r in pairs.values()),ambiguous_native=[hex(p) for p in sorted(conflicts)],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('Prepared',len(pairs),'links',len(rows),'images, ambiguous',list(map(hex,conflicts)),flush=True)
