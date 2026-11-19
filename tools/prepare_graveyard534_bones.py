"""Verify moving bone platform ownership/shared drawings and original palettes; no pixel fixes."""
import hashlib,json,struct
from pathlib import Path
from collections import Counter
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard522-enemies/report.json';r=bound(reference)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
pairs=[(0xc3b437,0xe69a6,0xc58e1c),(0xc3b466,0xe69fe,0xc58e36),(0xc3b491,0xe6a26,0xc58e50),(0xc3b4b6,0xe6a4e,0xc58e6a)]
votes={c:Counter() for c in range(1,16)};drawings=[]
def points(b):
    x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
for p,q,d in pairs:
    a=points(bitmap(s,snes_frame(s,p&0x3fffff),False,with_origin=True));b=points(bitmap(m,md_frame(m,q),True,with_origin=True))
    assert len(a.keys()^b.keys())<=2
    for k in a.keys()&b.keys():votes[a[k]][b[k]]+=1
    at=d&0x3fffff;assert s[at:at+3]==bytes.fromhex('d1d7c0') and int.from_bytes(s[at+6:at+9],'little')==p
    drawings.append(dict(native=hex(p),md=hex(q),descriptor=hex(d),shared_silhouette=True,retained_native_art=True))
native=struct.pack('<15H',*r['cgram'][241:256]);assert s[0x2f769:0x2f769+30]==native
palette=int.from_bytes(m[0x1cfdb4+2*48+44:0x1cfdb4+2*48+48],'big')
normal=[(c>>1&7)|((c>>5&7)<<3)|((c>>9&7)<<6) for c in struct.unpack_from('>64H',m,palette)];paths=[Path(__file__),reference]
for field in (14000,16000,18000):
    p=ROOT/f'build/md-next-levels-replay/capture-{field}/cram.bin';assert list(struct.unpack('<64H',p.read_bytes())[33:48])==normal[33:48];paths.append(p)
mapping=[0]+[votes[c].most_common(1)[0][0] if votes[c] else c for c in range(1,16)]
sha=hashlib.sha256(native).digest();meta=ROOT/'engine/runner/tlk_graveyard_bone_metadata.h'
meta.write_text('/* Original moving-platform ownership/palette metadata; no images/colors. */\nstatic const unsigned graveyard_bone_poses[]={'+','.join(hex(p) for p,q,d in pairs)+'};\nstatic const unsigned graveyard_bone_descriptors[]={'+','.join(hex(d) for p,q,d in pairs)+'};\nstatic const unsigned char graveyard_bone_palette_hash[32]={'+','.join('0x%02x'%x for x in sha)+'};\nstatic const unsigned char graveyard_bone_to_md[16]={'+','.join(map(str,mapping))+'};\n')
out=ROOT/'build/graveyard534-bones';out.mkdir(exist_ok=True);paths.append(meta)
(out/'report.json').write_text(json.dumps(dict(result='BONE_PLATFORMS_VERIFIED',pairs=drawings,native_palette=7,md_palette=2,index_map=mapping,scope='Original generic moving-platform callbackC0D7D1 and exact native descriptor/pose associations. Practical common silhouettes retained; no work on the originals one/two-pixel differences. Independent MD colors use existing prepared scene palette2.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PLATFORMS_VERIFIED',mapping,flush=True)
