"""Bind material original rule differences; distinguish collision headers from visual dimensions."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
assert s[0x16d9b:0x16da5]==bytes.fromhex('ad8ea61a1aa02a009100')
assert m[0x19fe5c:0x19fe72]==bytes.fromhex('4eb90018f34a323c0001d2402279ffff81c43341002a')
assert s[0x17fc4:0x17fcc]==bytes.fromhex('a02a00b1003a9100')
assert m[0x1a0f8e:0x1a0f94]==bytes.fromhex('04690001002a')
boxes=[]
for a,b in json.loads((ROOT/'tools/graveyard_vulture_pairs.json').read_text())['pairs']:
    n=struct.unpack_from('<4h',s,(int(a,16)&0x3fffff)+12);d=struct.unpack_from('>4h',m,int(b,16)+12)
    if n!=d:boxes.append(dict(native_pose=a,md_pose=b,native=n,md=d))
assert len(boxes)==4 and max(abs(x-y) for b in boxes for x,y in zip(b['native'],b['md']))>=12
assert s[0x2d265:0x2d276]==bytes.fromhex('ad6e008500a00a00b1008508ad68008500')
assert m[0x1a2c0a:0x1a2c26]==bytes.fromhex('2279ffffcd463229000a2279ffff81c43429000a044200743e01be42')
old=(ROOT/'build/graveyard617-gameplay-baseline/engine/generated/resources/pride_hitbox_map.h').read_text().splitlines();new=(ROOT/'engine/generated/resources/pride_hitbox_map.h').read_text().splitlines();assert all(x in new for x in old if x.startswith('{')) and sum(x.startswith('{') for x in new)==840
out=ROOT/'build/graveyard620-rules';out.mkdir(exist_ok=True);paths=[Path(__file__),ROOT/'tools/graveyard_vulture_pairs.json',ROOT/'engine/generated/resources/pride_hitbox_map.h',ROOT/'tools/pride_hitbox_catalog.py']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_RULE_DIFFERENCES_VERIFIED',health=dict(native=[2,3,4],md=[1,2,3],native_owner='C58CCA',md_owner='D13F6',hit_decrement=1),vulture_collision_bounds=boxes,pillar=dict(native='Compare Simba Y against pillar Y-116',md='Compare Simba Y against pillar Y-116',scope='Same ordinary height response; MD globalCD46 is the player, not current actor81C4. No pillar gameplay adapter warranted.'),preserved_existing_records=836,added_vulture_records=4,scope='Source evidence for meaningful gameplay choices; native/MD visual width/height fields are not used as collision bounds. Bone waits30/26 and regular hyena initial health difficulty+1 already agree. One-pixel bone jitter is deliberately skipped; broader universal AI parity is not claimed.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('VERIFIED',boxes,flush=True)
