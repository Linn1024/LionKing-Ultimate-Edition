"""Verify installer-only gameplay data change preserves existing art and all other prepared gameplay."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
def unpack(path):
    raw=path.read_bytes();at=192+416+17792;images={}
    for _ in range(struct.unpack_from('<I',raw,20)[0]):
        pose,a,b=struct.unpack_from('<3I',raw,at);at+=12;images[pose]=raw[at:at+a+b];at+=a+b
    gameplay=raw[at:];sizes=struct.unpack_from('<4I',gameplay,16);records=[];at=32
    for n in sizes:records.append(gameplay[at:at+n]);at+=n
    boxes={}
    for n in range(struct.unpack_from('<I',records[2])[0]):
        row=records[2][4+n*26:4+(n+1)*26];boxes[struct.unpack_from('<I',row)[0]]=row
    return raw[192:192+416+17792],images,records,boxes,raw[88:120]
helper=ROOT/'build/graveyard619-helper/build-report.json';bound(helper)
a=unpack(ROOT/'build/graveyard529-helper/sprites.assets');b=unpack(helper.parent/'sprites.assets')
added=[v for k,v in b[3].items() if k not in a[3]]
checks=dict(palettes_unchanged=a[0]==b[0],all_images_unchanged=a[1]==b[1],other_gameplay_unchanged=all(a[2][i]==b[2][i] for i in (0,1,3)),all_836_old_bounds_unchanged=len(a[3])==836 and all(b[3].get(k)==v for k,v in a[3].items()),only_four_valid_vulture_records=len(added)==4 and all(row[8:10]==bytes((4,1)) for row in added),address_policy_changed=a[4]!=b[4])
out=ROOT/'build/graveyard624-assets';out.mkdir(exist_ok=True);paths=[Path(__file__),helper]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
