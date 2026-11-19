"""Verify newly prepared body words, preserved earlier records and unchanged art/palettes."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1008-data';out.mkdir(exist_ok=True)
def unpack(path):
 data=path.read_bytes();at=192+416+17792;images={}
 for _ in range(struct.unpack_from('<I',data,20)[0]):p,n,k=struct.unpack_from('<3I',data,at);at+=12;images[p]=data[at:at+n+k];at+=n+k
 g=data[at:];sizes=struct.unpack_from('<6I',g,16);at=40;sections=[]
 for n in sizes:sections.append(g[at:at+n]);at+=n
 assert at==len(g);return data,images,sections
def boxes(data):
 n=struct.unpack_from('<I',data)[0];assert len(data)==4+n*26;return {struct.unpack_from('<I',data,4+i*26)[0]:data[4+i*26:4+(i+1)*26] for i in range(n)}
old,oi,os=unpack(ROOT/'build/bonus985-sprite-helper/sprites.assets');new,ni,ns=unpack(ROOT/'build/remaining1007-helper/sprites.assets');ob=boxes(os[2]);nb=boxes(ns[2]);spec=json.loads((ROOT/'build/remaining1005-bounds/report.json').read_text())['pairs'];matches=[]
for p in spec:
 r=nb[int(p['snes'],16)];matches.append(r[8]==5 and r[9]==1 and struct.unpack_from('<4h',r,10)==tuple(p['native']) and struct.unpack_from('<4h',r,18)==tuple(p['external']))
checks=dict(all1466_images_preserved=oi==ni,shared_palettes_and_death_bank_preserved=old[192:18400]==new[192:18400],other_five_sections_preserved=all(os[i]==ns[i] for i in range(6) if i!=2),previous924_bounds_preserved=all(nb[k]==v for k,v in ob.items()),all56_original_scar_bounds=all(matches),records980=len(nb)==980)
paths=[Path(__file__),ROOT/'build/remaining1005-bounds/report.json',ROOT/'build/remaining1007-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
