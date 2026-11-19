"""Verify shared monkey artwork and native palette identities for a live MD palette choice."""
import json,hashlib,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait435-animals/report.json';ref=bound(reference)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
ram=(ROOT/ref['native_bank_snapshot']).read_bytes();work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:]=ram[0x10000:]
external={}
for p in range(0xce000,0xd1000,2):
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:external.setdefault(b,[]).append(p)
pairs=[]
for p in range(0x43e00,0x44900):
    if work[p]>127:continue
    f=snes_frame(work,p)
    if not f:continue
    b=bitmap(work,f,False,with_origin=True)
    if b in external:pairs.append(dict(native_pose=hex(p|0xc00000),md_poses=[hex(n) for n in external[b]],origin=b[:2],size=b[2:4]))
assert pairs
known={int(p['native_pose'],16) for p in pairs};live=[];paths=[Path(__file__),reference]
for field in (5000,6008,7000,8008,9000,10008,11000,12008):
    path=ROOT/f'build/cant-wait-native/aot/hl_wram_{field}.bin'
    if not path.exists():continue
    r=path.read_bytes();paths.append(path);w=lambda a:int.from_bytes(r[a:a+2],'little');ptr=lambda a:int.from_bytes(r[a:a+3],'little')
    for actor in range(0x8000,0xff80,2):
        draw=w(actor+12)
        if not 0x2000<=draw<=0xffe0 or w(draw+4)!=actor+8:continue
        pose=ptr(draw+10)
        if pose in known:live.append(dict(field=field,descriptor=hex(ptr(actor+4)),action=hex(ptr(actor+48)),pose=hex(pose),palette=(w(draw+8)>>9)&7))
hashes={}
for phase,start in (('initial',0x50b7a),('alternate',0x601b5)):
    hashes[phase]={str(bank):hashlib.sha256(s[start+(128+bank*16)*2:start+(128+bank*16+1)*2+30]).hexdigest() for bank in (2,3)}
out=ROOT/'build/cant-wait436-monkeys';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='SHARED_ART_VERIFIED',pairs=pairs,live=live,native_palette_visible_hashes=hashes,scope='Exact anchored indexed art, retained real native draw ownership and original native initial/alternate OBJ palette fingerprints. Palette choice only; no animation/gameplay adapter.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('pairs',len(pairs),'live',live,'palette hashes',hashes,flush=True)
