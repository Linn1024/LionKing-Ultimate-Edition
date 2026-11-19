"""Verify exact ostrich frames; retain only address metadata in maintained code."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait445-draws/report.json';r=bound(reference)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
images={}
for p in range(0xcfa00,0xd1000,2):
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:images.setdefault(b,[]).append(p)
pairs=[]
for p in range(0x3ad00,0x3b400):
    if s[p]>127:continue
    f=snes_frame(s,p)
    if not f:continue
    b=bitmap(s,f,False,with_origin=True)
    if b in images:pairs.append(dict(native_pose=hex(p|0xc00000),md_poses=[hex(q) for q in images[b]],origin=b[:2],size=b[2:4]))
# Airborne poses live outside the original bounded running-frame scan.
for native,external in [(0x1d6b2,0xd082a),(0x1d725,0xd0902),(0x1d788,0xd09aa)]:
    a=bitmap(s,snes_frame(s,native),False,with_origin=True)
    b=bitmap(m,md_frame(m,external),True,with_origin=True)
    assert a==b and all(int(p['native_pose'],16)!=(native|0xc00000)for p in pairs)
    pairs.append(dict(native_pose=hex(native|0xc00000),md_poses=[hex(external)],origin=a[:2],size=a[2:4]))
head=bound(ROOT/'build/fidelity4436-ostrich-head-art/report.json')
assert len(head['rows'])==23
for row in head['rows']:
    assert row['md_exact_anchored_matches']
    pairs.append(dict(native_pose=row['native_pose'],md_poses=row['md_exact_anchored_matches'],origin=row['origin'],size=row['size']))
pairs.sort(key=lambda p:int(p['native_pose'],16))
live=[a for a in r['actors'] if a['descriptor'] in ('0xc58c20','0xc58c2c')]
assert len(live)>=4 and {a['native_palette'] for a in live}=={2}
assert all(any(a['native_pose']==p['native_pose'] for p in pairs) for a in live)
header=ROOT/'engine/runner/tlk_cw_ostrich_metadata.h';header.write_text('/* Exact anchored/indexed ostrich frame correspondences, no game assets. */\nstatic const unsigned cw_ostrich_poses[]={'+','.join(p['native_pose'] for p in pairs)+'};\nstatic const unsigned cw_ostrich_descriptors[]={0xc58c20,0xc58c2c,0xc58c38};\n')
out=ROOT/'build/cant-wait447-ostrich';out.mkdir(exist_ok=True)
paths=[Path(__file__),reference,header]
(out/'report.json').write_text(json.dumps(dict(result='VERIFIED_METADATA',pairs=pairs,live=live,scope='Original shared ostrich frame artwork, both ordinary native actor descriptors and OBJ bank2. Colors use the existing prepared/live level palette; gameplay unchanged.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('ostrich shared frames',len(pairs),'live',len(live),flush=True)
