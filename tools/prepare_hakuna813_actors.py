"""Prepare reviewed later actor metadata and all matched gorilla action drawings."""
import collections,json,re,runpy,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_sprite_catalog import md_frame,bitmap
out=ROOT/'build/hakuna813-actors';out.mkdir(exist_ok=True)
gorilla=ROOT/'tools/hakuna_gorilla_pairs.json';spec=json.loads(gorilla.read_text());pairs={int(r['snes'],16):r for r in spec['pairs']};sample=next(iter(pairs.values()))
for p in json.loads((ROOT/'build/hakuna810-actions/report.json').read_text())['additional_pairs']:
 key=int(p['snes'],16);pairs[key]=dict(p,native_to_md=sample['native_to_md'],md_to_native=sample['md_to_native'],basis='corresponding original throwing/turning/landing action phases; drawing choice only')
spec['pairs']=[pairs[p] for p in sorted(pairs)];assert len(pairs)==55;gorilla.write_text(json.dumps(spec,indent=2)+'\n')
d=runpy.run_path(str(ROOT/'tools/audit_hakuna792_actors.py'));native=d['native'];external=d['external'];image=d['image'];ns=d['ns'];ms=d['ms'];reports=d['reports'];m=d['m'];s=d['s']
header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=header.read_text();a=text.index('\n{');b=text.index('\n};',a);old={int(re.match(r'\{0x([0-9a-f]+),',line)[1],16):line for line in text[a+1:b].splitlines()};rows=dict(old)
def old_role(p):
 match=re.search(r'\}\},(\d+),(\d+),(\d+),',old.get(p,''));return int(match[1]) if match else 0
def rgb(c):return tuple((c>>sh)&31 for sh in (0,5,10))
def distance(a,b):return sum(w*(x-y)**2 for x,y,w in zip(rgb(a),rgb(b),(3,6,2)))
def crop(b):
 x0,y0,w,h,pix=b;points=[(i%w,i//w) for i,c in enumerate(pix) if c];x=min(x for x,y in points);y=min(y for x,y in points);right=max(x for x,y in points)+1;bottom=max(y for x,y in points)+1
 return right-x,bottom-y,bytes(pix[j*w+i] for j in range(y,bottom) for i in range(x,right))
def mapping(a,b,ca,cb):
 a=crop(a);b=crop(b);assert a[:2]==b[:2] and bytes(bool(c) for c in a[2])==bytes(bool(c) for c in b[2]);votes=collections.defaultdict(collections.Counter)
 for x,y in zip(a[2],b[2]):
  if x and y:votes[x][y]+=1
 return [0]+[votes[c].most_common(1)[0][0] if votes[c] else min(range(1,16),key=lambda n:distance(ca[c],cb[n])) for c in range(1,16)]
families=[(5,'c58ee4','0e962e',14,0,0),(5,'c58ed8','0e963c',14,0,0),(5,'c58e9c','0e96a4',14,0,3),(5,'c58afc','0e9166',15,0,0),(5,'c58aec','0e914c',15,0,0),(5,'c58981','09792c',17,0,0),(5,'c5889a','097836',17,0,0),(5,'c588a6','097844',17,0,0),(6,'c58eb4','111f88',14,7,3),(6,'c58ea8','111f7a',14,7,3),(6,'c586d8','112330',18,5,0),(6,'c588dd','112564',15,2,2),(6,'c588fd','112598',15,2,2),(6,'c587e4','1125e4',15,2,2),(6,'c587f0','1125f2',15,2,2),(6,'c587fc','112600',15,2,2),(6,'c58808','11260e',15,2,2),(6,'c58844','112554',15,2,2),(6,'c586f0','111f00',15,4,2),(6,'c586cc','0950e0',16,0,0),(6,'c588b2','097836',17,0,0),(6,'c588be','097844',17,0,0)]
prepared={};coverage=[]
for level,desc,mdesc,role,nb,mb in families:
 family=next((r for r in reports if r['level']==level and r['native_descriptor']==desc),None)
 if not family:continue
 native_colors=next(r['colors'] for r in ns if r['descriptor']==desc and int(r['palette'])==nb and ((int(r['frame'])<36500)==(level==5)))
 ca=[int(native_colors[i:i+4],16) for i in range(0,64,4)];pal=int.from_bytes(m[0x1cfdb4+level*48+44:0x1cfdb4+level*48+48],'big')+mb*32
 def mdcolor(c):
  v=[((c>>sh)&7)*4+(((c>>sh)&7)>>2) for sh in (1,5,9)];return v[0]|v[1]<<5|v[2]<<10
 cb=[mdcolor(int.from_bytes(m[pal+i*2:pal+i*2+2],'big')) for i in range(16)];count=0
 for pair in family['pairs']:
  p=int(pair['snes'],16)&0x3fffff
  if int(pair['native_palette'])!=nb or old_role(p):continue
  qs=[q for q in pair['md'] if any(r['pose']==q and r['descriptor']==mdesc for r in ms if int(r['level'])==level)] or pair['md']
  oldq=int(re.match(r'\{0x[0-9a-f]+, 0x([0-9a-f]+),',old[p])[1],16) if p in old else None
  q=oldq if oldq is not None and f'{oldq:06x}' in qs else int(qs[0],16)
  na=image(native[level],hex(p),False);ma=image(external[level],hex(q),True)
  if not na or not ma:continue
  f=mapping(na,ma,ca,cb);r=mapping(ma,na,cb,ca)
  row=dict(snes=hex(p),md=hex(q),role=role,native_palette=nb,md_palette=mb,native_to_md=f,md_to_native=r,basis=pair['basis'],owners=[dict(level=level,descriptor='0x'+desc)])
  if p in prepared:
   previous=prepared[p];assert all(previous[k]==row[k] for k in ('role','native_palette','md_palette','native_to_md','md_to_native')),(hex(p),previous,row)
   previous['owners']+=row['owners']
  else:prepared[p]=row
  count+=1
 coverage.append(dict(level=level,descriptor=desc,role=role,linked=count,observed=family['native'],remaining=family['missing']))
late=dict(scope='Reviewed original Hakuna/Destiny actor frame/palette links with exact scene/descriptor ownership; native gameplay independent.',pairs=[prepared[p] for p in sorted(prepared)])
(ROOT/'tools/hakuna_destiny_actor_pairs.json').write_text(json.dumps(late,indent=2)+'\n')
for pair in spec['pairs']+late['pairs']:
 p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16);role=pair.get('role',13);nb=pair.get('native_palette',6);mb=pair.get('md_palette',3);frame=md_frame(m,q);assert frame
 x,y,w,h,pix=bitmap(m,frame,True,with_origin=True)
 rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{role},{nb},{mb}, {{'+','.join(map(str,pair['md_to_native']))+'}, {'+','.join(map(str,pair['native_to_md']))+'}},'
header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:])
changed=set(prepared)|{int(r['snes'],16)&0x3fffff for r in spec['pairs']};checks=dict(gorilla55=len(pairs)==55,other_metadata_preserved=all(rows[k]==v for k,v in old.items() if k not in changed),all_previous_semantic_roles_preserved=all(rows[k]==v for k,v in old.items() if old_role(k) and old_role(k)!=13))
paths=[Path(__file__),gorilla,ROOT/'tools/hakuna_destiny_actor_pairs.json',header]
(out/'report.json').write_text(json.dumps(dict(result='PREPARED' if all(checks.values()) else 'FAIL',checks=checks,old_count=len(old),new_count=len(rows),late_poses=len(prepared),coverage=coverage,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,'images',len(old),'->',len(rows),'actor links',len(prepared))
