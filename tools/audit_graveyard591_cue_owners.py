"""Bind exact original cue actors; sparse nearby snapshots are not ownership evidence."""
import collections,csv,json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
source=ROOT/'build/graveyard590-original-context';frames=json.loads((source/'frames.json').read_text());levels={r['frame']:r['level'] for r in frames};records=[];counts=collections.Counter();paths=[Path(__file__),source/'commands.csv',source/'frames.json']
for row in csv.DictReader((source/'commands.csv').open()):
    field=int(row['frame'])
    if levels.get(field)!=2 or int(row['selector']) not in (2,19):continue
    p=source/f'capture-{field}/work_ram.bin';ram=p.read_bytes();paths.append(p)
    w=lambda a:struct.unpack_from('<H',ram,a&65535)[0];a=lambda p:(w(p)<<16|w(p+2))&0xffffff
    actor=int(row['actor'],16);draw=w(actor+12);owned=0x8000<=draw<=0xffe8 and w(draw+4)==actor+8
    rec=dict(frame=field,selector=int(row['selector']),value=int(row['value']),caller=row['outer_caller'],actor=hex(actor),descriptor=hex(a(actor+4)),sound_state=row['actor_state'],snapshot_state=hex(a(actor+0x30)),draw_owned=owned,pose=hex(a(draw+10)) if owned else None,counter=w(actor+0x2c),xy=[w(actor+8),w(actor+10)])
    records.append(rec);counts[(rec['selector'],rec['value'],rec['caller'],rec['descriptor'],rec['sound_state'])]+=1
out=ROOT/'build/graveyard591-cue-owners';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='EXACT_ORIGINAL_OWNERS',records=records,counts=[dict(selector=k[0],value=k[1],caller=k[2],descriptor=k[3],state=k[4],count=v) for k,v in counts.items()],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in dict.fromkeys(paths)}),indent=2)+'\n');print(list(counts.items()),flush=True)
