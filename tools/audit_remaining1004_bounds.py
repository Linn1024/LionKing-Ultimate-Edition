"""Review Scar collision mappings against every valid original frame in its bank."""
import collections,hashlib,json,struct
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1004-bounds';out.mkdir(exist_ok=True);m=(ROOT/'Lion King, The (World).md').read_bytes();s=(ROOT/'Lion King, The (USA).sfc').read_bytes()
def key(p):
 b=bitmap(m,md_frame(m,p),True,with_origin=True);x,y,w,h,data=b;pts=[(i%w,i//w) for i,c in enumerate(data) if c]
 if not pts:return None
 left=min(x for x,y in pts);right=max(x for x,y in pts)+1;top=min(y for x,y in pts);bottom=max(y for x,y in pts)+1
 return (x+left,y+top,right-left,bottom-top,bytes(data[y*w+x] for y in range(top,bottom) for x in range(left,right)))
groups=collections.defaultdict(list)
for p in range(0x17a400,0x17f000):
 if md_frame(m,p):
  try:k=key(p)
  except (IndexError,ValueError):continue
  if k:groups[k].append(p)
rows=[];safe=[]
for r in json.loads((ROOT/'tools/pride_actor_pairs.json').read_text())['pairs']:
 if r['role']!=20:continue
 a=int(r['snes'],16)&0x3fffff;b=int(r['md'],16);candidates=groups[key(b)];assert b in candidates
 boxes={struct.unpack_from('>4h',m,p+12) for p in candidates};native=struct.unpack_from('<4h',s,a+12);external=struct.unpack_from('>4h',m,b+12)
 row=dict(snes=hex(a),md=hex(b),role=5,native=list(native),external=list(external),candidates=[hex(p) for p in candidates],unambiguous=len(boxes)==1,max_edge_delta=max(abs(x-y) for x,y in zip(native,external)))
 rows.append(row)
 if row['unambiguous']:safe.append(dict(snes=hex(a),md=hex(b),role=5))
checks=dict(all_original_candidates_reviewed=all(r['candidates'] for r in rows),unique_bounds_available=bool(safe))
(out/'safe-pairs.json').write_text(json.dumps(dict(pairs=safe),indent=2)+'\n')
paths=[Path(__file__),ROOT/'tools/pride_actor_pairs.json']
(out/'report.json').write_text(json.dumps(dict(result='REVIEWED' if all(checks.values()) else 'INCOMPLETE',checks=checks,total=len(rows),safe=len(safe),different_safe=sum(r['unambiguous'] and r['native']!=r['external'] for r in rows),max_safe_delta=max(r['max_edge_delta'] for r in rows if r['unambiguous']),pairs=rows,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(len(rows),'poses;',len(safe),'unambiguous;',sum(r['unambiguous'] and r['native']!=r['external'] for r in rows),'different',flush=True)
