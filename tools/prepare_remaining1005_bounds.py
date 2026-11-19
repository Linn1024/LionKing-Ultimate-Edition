"""Append reviewed adult-hyena body rectangles without changing earlier pose policies."""
import json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1005-bounds';out.mkdir(exist_ok=True);p=ROOT/'engine/generated/resources/pride_hitbox_map.h';s=p.read_text();a=s.index('\n{');b=s.index('\n};',a);old={int(re.match(r'\{0x([0-9a-f]+),',l)[1],16):l for l in s[a+1:b].splitlines()};rows=dict(old);sn=(ROOT/'Lion King, The (USA).sfc').read_bytes();md=(ROOT/'Lion King, The (World).md').read_bytes();pairs=[]
for r in json.loads((ROOT/'tools/scar_bounds_pairs.json').read_text())['pairs']:
 if r['role']!=5:continue
 x=int(r['snes'],16)&0x3fffff;y=int(r['md'],16);line=f'{{0x{x:x},0x{y:x},5}},';assert x not in old or old[x]==line;rows[x]=line;n=struct.unpack_from('<4h',sn,x+12);m=struct.unpack_from('>4h',md,y+12);pairs.append(dict(snes=hex(x),md=hex(y),native=list(n),external=list(m),max_edge_delta=max(abs(a-b) for a,b in zip(n,m))))
p.write_text(s[:a+1]+'\n'.join(rows[k] for k in sorted(rows))+s[b:]);checks=dict(previous_policy_preserved=all(rows[k]==v for k,v in old.items()),source_bounds_valid=all(r['native'][0]<=r['native'][2] and r['native'][1]<=r['native'][3] and r['external'][0]<=r['external'][2] and r['external'][1]<=r['external'][3] for r in pairs));paths=[Path(__file__),p,ROOT/'tools/pride_hitbox_catalog.py',ROOT/'tools/scar_bounds_pairs.json']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED' if all(checks.values()) else 'FAIL',checks=checks,old_records=len(old),new_records=len(rows),scar_records=len(pairs),different=sum(r['native']!=r['external'] for r in pairs),max_edge_delta=max(r['max_edge_delta'] for r in pairs),pairs=pairs,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(len(old),'->',len(rows),len(pairs),'Scar records;',sum(r['native']!=r['external'] for r in pairs),'different',flush=True)
