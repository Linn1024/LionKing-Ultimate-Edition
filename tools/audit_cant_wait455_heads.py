"""Decode the remaining level-two head frames and find anchored MD counterparts.

Uses retained original memory, no replay or runtime changes. Matching candidates
need animal/animation ownership before an adapter is enabled.
"""
import json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait455-heads';out.mkdir(exist_ok=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
snapshot=ROOT/'build/cant-wait-native/aot/hl_wram_5000.bin';ram=snapshot.read_bytes();work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:]=ram[0x10000:]
md={}
for p in range(0,len(m)-40,2):
    if m[p] or m[p+1]>31:continue
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:md[p]=b
def sparse(b,mask=False):
    x,y,w,h,data=b
    return {(x+i,y+j):(1 if mask else data[j*w+i]) for j in range(h) for i in range(w) if data[j*w+i]}
rows=[];images=[]
for p in range(0x3c900,0x3d100):
    if work[p]>127:continue
    f=snes_frame(work,p)
    if not f:continue
    b=bitmap(work,f,False,with_origin=True)
    if len(b)!=5:continue
    a=sparse(b);candidates=[]
    for q,c in md.items():
        if abs(b[2]-c[2])>8 or abs(b[3]-c[3])>8:continue
        z=sparse(c);mask=len(a.keys()^z.keys());indexed=sum(a.get(k,0)!=z.get(k,0) for k in a.keys()|z.keys())
        candidates.append((mask,indexed,q))
    candidates.sort();best=candidates[:3];rows.append(dict(native_pose=hex(p|0xc00000),origin=b[:2],size=b[2:4],candidates=[dict(md_pose=hex(q),mask_difference=d,indexed_difference=c) for d,c,q in best]));images.append((hex(p|0xc00000),b))
    if best:images.append((hex(best[0][2]),md[best[0][2]]))
sheet=Image.new('RGB',(800,max(1,(len(images)+7)//8)*145),(25,35,50));draw=ImageDraw.Draw(sheet)
for i,(label,b) in enumerate(images):
    x=i%8*100;y=i//8*145;image=Image.new('RGB',b[2:4]);image.putdata([(v*17,)*3 if v else (25,35,50) for v in b[4]]);sheet.paste(image,(x,y+18));draw.text((x,y),label,fill='white')
sheet.save(out/'heads.png')
paths=[Path(__file__),snapshot]
(out/'report.json').write_text(json.dumps(dict(result='CANDIDATES',frames=rows,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'heads.png':digest(out/'heads.png')}),indent=2)+'\n')
print('frames',len(rows),rows,flush=True)
