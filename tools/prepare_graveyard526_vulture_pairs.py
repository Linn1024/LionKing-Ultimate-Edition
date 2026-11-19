"""Pair original vulture animation phases; report unmapped records before promoting metadata."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
r=json.loads((ROOT/'build/graveyard525-vulture-streams/report.json').read_text());ns={int(x['offset'],16):x['records'] for x in r['native_streams']};ms={int(x['offset'],16):x['records'] for x in r['md_streams']}
pairs={};streams=[]
for a,b in ((0x27f7a,0xd1470),(0x27f85,0xd147c),(0x27ffc,0xd14e8),(0x2803c,0xd1512),(0x2805a,0xd1530),(0x28068,0xd153e),(0x281d9,0xd15e2),(0x2820f,0xd161e),(0x28244,0xd165a)):
    one,two=ns[a],ms[b];assert len(one)==len(two)
    for x,y in zip(one,two):
        p,q=int(x[1],16),int(y[1],16)
        assert p not in pairs or pairs[p]==q;pairs[p]=q
    streams.append(dict(native=hex(a),md=hex(b),native_durations=[x[0] for x in one],md_durations=[x[0] for x in two]))
# The actual native/MD idle and landing initializers refer to these records.
for p,q in ((0xc3fa2d,0xe81ce),(0xc3fa60,0xe8206),(0xc3fa93,0xe823e),(0xc3faca,0xe8276),(0xc3fb31,0xe82fe),(0xc3fb6c,0xe8356)):
    assert p not in pairs;pairs[p]=q
out=ROOT/'build/graveyard526-vulture-pairs';out.mkdir(exist_ok=True);paths=[Path(__file__),ROOT/'build/graveyard525-vulture-streams/report.json']
missing=[x for x in r['native_frames'] if int(x,16) not in pairs]
(out/'report.json').write_text(json.dumps(dict(result='ORDERED_PHASE_PAIRS',pairs=[[hex(p),hex(q)] for p,q in sorted(pairs.items())],streams=streams,missing=missing,scope='Original animation-family phase correspondence. Native timing retained; artwork need not be literally identical and landing phases differ between originals. Direct initializer poses require independent ownership verification.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PAIRS',len(pairs),'MISSING',missing,flush=True)
