"""Inspect RAM-backed giraffe head images using full retained native WRAM.

Read-only; no game replays, asset promotion or static pose assumptions.
"""
import hashlib,json
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait469-giraffe';out.mkdir(exist_ok=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
md={}
for p in range(0xd10f0,0xd1600,2):
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:md[p]=b
def points(b):
    x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
variants={};observed=[];paths=[Path(__file__)]
for field in range(5000,6201,16):
    path=ROOT/f'build/cant-wait-native/aot/hl_wram_{field}.bin'
    if not path.exists():continue
    r=path.read_bytes();paths.append(path);work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3e0000:]=r
    for pose in (0xc3cef7,0xc3cfbe):
        f=snes_frame(work,pose&0x3fffff);assert f
        b=bitmap(work,f,False,with_origin=True)
        if len(b)!=5:continue
        key=(pose,hashlib.sha256(b[4]).hexdigest());observed.append(dict(field=field,pose=hex(pose),image_sha256=key[1]))
        if key in variants:continue
        a=points(b);candidates=[]
        for q,c in md.items():
            z=points(c);candidates.append((len(a.keys()^z.keys()),sum(a.get(k,0)!=z.get(k,0) for k in a.keys()|z.keys()),q))
        candidates.sort();variants[key]=(b,candidates[:2])
images=[];records=[]
for (pose,sha),(b,candidates) in variants.items():
    records.append(dict(native_pose=hex(pose),sha256=sha,origin=b[:2],size=b[2:4],candidates=[dict(md_pose=hex(q),mask_difference=a,index_difference=z) for a,z,q in candidates]));images.append((hex(pose),b))
    if candidates:images.append((hex(candidates[0][2]),md[candidates[0][2]]))
sheet=Image.new('RGB',(640,max(1,(len(images)+7)//8)*85),(25,35,50));d=ImageDraw.Draw(sheet)
for i,(label,b) in enumerate(images):
    x=i%8*80;y=i//8*85;im=Image.new('RGB',b[2:4]);im.putdata([(v*17,)*3 if v else (25,35,50) for v in b[4]]);sheet.paste(im,(x,y+18));d.text((x,y),label,fill='white')
sheet.save(out/'giraffe.png')
(out/'report.json').write_text(json.dumps(dict(result='RAM_ART_INVENTORIED',variants=records,observations=observed,md_frames=[hex(q) for q in md],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'giraffe.png':digest(out/'giraffe.png')}),indent=2)+'\n')
print('MD frames',list(map(hex,md)),'native variants',len(records),records[:8],flush=True)
