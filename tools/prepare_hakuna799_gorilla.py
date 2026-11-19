"""Freeze reviewed original gorilla frame links and update local generated metadata.

Only addresses, dimensions and color correspondences are tracked, not pictures
or cartridge instructions. Fresh catalogs use hakuna_sprite_catalog as well.
"""
import json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna799-gorilla';out.mkdir(exist_ok=True)
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes()
r=json.loads((ROOT/'build/hakuna798-streams/report.json').read_text());ns={int(x['address'],16):x['frames'] for x in r['groups']['snes']};ms={int(x['address'],16):x['frames'] for x in r['groups']['md']};links={};basis={}
for a,b,skip,count in [(0x27a77,0xe92c0,0,12),(0x27c42,0xe9404,0,4),(0x27c7c,0xe9428,0,4),(0x27c8e,0xe943a,0,5),(0x27cf9,0xe948a,0,9),(0x27d21,0xe94f2,1,8),(0x27db9,0xe9530,0,36),(0x27e4b,0xe95d2,0,4)]:
 for n,z in zip(ns[a][:count],ms[b][skip:skip+count]):
  assert n['duration']==z['duration'];p=int(n['pose'],16);q=int(z['pose'],16)
  assert p not in links or links[p]==q;links[p]=q;basis[p]=f'original action stream phases {a:06x}/{b:06x}'
for np,mp,p,q in [(0x27aea,0xe931d,0xc03104,0x10bfb4),(0x27bf6,0xe93cd,0xc02e3b,0x10bbcc),(0x27d9e,0xe9519,0xc02c6f,0x10b9fc),(0x27da4,0xe951f,0xc01fba,0x10a89c)]:
 assert int.from_bytes(s[np:np+3],'little')==p and int.from_bytes(m[mp:mp+3],'big')==q and s[np-1]==m[mp-1]
 links[p]=q;basis[p]=f'corresponding action-key pose {np:06x}/{mp:06x}'
assert len(links)==37
native=struct.unpack_from('<16H',s,0x607b9);palette=struct.unpack_from('>I',m,0x1cfdb4+5*48+44)[0]+96
def color(c):
 v=[((c>>sh)&7)*4+(((c>>sh)&7)>>2) for sh in (1,5,9)];return v[0]|v[1]<<5|v[2]<<10
md=[color(c) for c in struct.unpack_from('>16H',m,palette)]
def distance(a,b):return sum(weight*(((a>>sh)&31)-((b>>sh)&31))**2 for sh,weight in ((0,3),(5,6),(10,2)))
def mapping(a,b):return [0]+[min(range(1,16),key=lambda j:distance(a[i],b[j])) for i in range(1,16)]
forward=mapping(native,md);reverse=mapping(md,native)
spec=dict(scope='Original Hakuna gorilla artwork paired through action phases; native timing/gameplay independent.',pairs=[dict(snes=hex(p),md=hex(q),native_to_md=forward,md_to_native=reverse,basis=basis[p]) for p,q in sorted(links.items())])
(ROOT/'tools/hakuna_gorilla_pairs.json').write_text(json.dumps(spec,indent=2)+'\n')
header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=header.read_text();a=text.index('\n{');b=text.index('\n};',a);old={int(re.match(r'\{0x([0-9a-f]+),',line)[1],16):line for line in text[a+1:b].splitlines()};rows=dict(old)
for p,q in links.items():
 f=md_frame(m,q);assert f;image=bitmap(m,f,True,with_origin=True);x,y,w,h,_=image
 key=p&0x3fffff;rows[key]=f'{{0x{key:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},13,6,3, {{'+','.join(map(str,reverse))+'}, {'+','.join(map(str,forward))+'}},'
header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:])
checks=dict(all_observed_gorilla_poses=len(links)==37,other_metadata_preserved=all(rows[k]==v for k,v in old.items() if k not in {p&0x3fffff for p in links}))
paths=[Path(__file__),ROOT/'tools/hakuna_gorilla_pairs.json',ROOT/'tools/hakuna_sprite_catalog.py',header]
(out/'report.json').write_text(json.dumps(dict(result='PREPARED' if all(checks.values()) else 'FAIL',checks=checks,old_images=len(old),new_images=len(rows),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,'images',len(old),'->',len(rows))
