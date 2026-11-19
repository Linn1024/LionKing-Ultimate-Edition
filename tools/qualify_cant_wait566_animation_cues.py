"""Verify original animation-owned sounds and exact take-off actor identity."""
import csv,json,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
ostrich=ROOT/'build/cant-wait447-ostrich/report.json';pairs={int(x['native_pose'],16):[int(p,16) for p in x['md_poses']] for x in bound(ostrich)['pairs']}
p=0xb9026;tokens=[];markers=[]
while m[p]!=255:
    if m[p]==253:assert m[p+1]==1;markers.append(len(tokens));p+=2;continue
    tokens.append((m[p],int.from_bytes(m[p+1:p+4],'big')));p+=4
native=[(s[p],int.from_bytes(s[p+1:p+4],'little')) for p in range(0x26c41,0x26c6d,4)]
assert len(native)==len(tokens)==11 and markers==[0,5,10]
assert all(a[0]==b[0]==3 and b[1] in pairs[a[1]] for a,b in zip(native,tokens))
assert s[0x26cbd:0x26cc1]==bytes.fromhex('ffb96cc2')
assert s[0x2585f:0x25863]==bytes.fromhex('ff4f58c2')
context=ROOT/'build/cant-wait563-original-context';records=[]
for row in csv.DictReader((context/'commands.csv').open()):
    if row['selector']!='19' or row['value']!='5':continue
    ram=(context/f"capture-{row['frame']}/work_ram.bin").read_bytes();w=lambda a:struct.unpack_from('<H',ram,a&65535)[0];l=lambda a:(w(a)<<16|w(a+2))&0xffffff
    actor=int(row['actor'],16);draw=w(actor+12)
    assert l(actor+4)==0xb8ca6 and w(draw+4)==actor+8 and row['actor_state']=='19fd48'
    records.append(dict(frame=int(row['frame']),descriptor=hex(l(actor+4)),pose=hex(l(draw+10))))
assert len(records)==6
assert int.from_bytes(m[0xb8ca6:0xb8caa],'big')==0x19fb02
assert s[0x58814:0x58817]==bytes.fromhex('d2ecc2')
out=ROOT/'build/cant-wait566-animation-cues';out.mkdir(exist_ok=True)
paths=[Path(__file__),ostrich,ROOT/'tools/audit_cant_wait563_original_context.py',context/'commands.csv']
(out/'report.json').write_text(json.dumps(dict(result='VERIFIED',running_markers=markers,running_frames=11,takeoffs=records,scope='Exact six original take-off events all own flying descriptorB8CA6, not stale monkey slots. Native flying action C2ECD2/C2EF2E has the same silent transition. Native/MD ostrich running streams share11 anchored poses and three-update durations; observe the three MD markers without guest writes. First jump/take-off tokens are outside their animation loops.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('VERIFIED',flush=True)
