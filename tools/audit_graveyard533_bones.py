"""Inspect actual bone-debris drawings against original MD bone families; no runtime mapping yet."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
s0=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');s=bytearray(s0);s.extend(bytes(0x400000-len(s)));s[0x3e0000:]=(ROOT/'build/graveyard519-wram/wram.bin').read_bytes()
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
def mask(b):
    x,y,w,h,data=b;return {(i,j) for j in range(h) for i in range(w) if data[j*w+i]}
native={p:bitmap(s,snes_frame(s,p),False,with_origin=True) for p in (0x3b437,0x3b466,0x3b491,0x3b4b6)}
md={}
for q in range(0xe66fe,0xe6ed0,2):
    f=md_frame(m,q)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:md[q]=b
records=[];images=[]
for p,a in native.items():
    near=sorted((len(mask(a)^mask(b)),q) for q,b in md.items())[:2]
    records.append(dict(native_pose=hex(p|0xc00000),candidates=[dict(md_pose=hex(q),mask_difference=d,native_origin=a[:2],md_origin=md[q][:2]) for d,q in near]));images.append((hex(p),a));images.append((hex(near[0][1]),md[near[0][1]]))
sheet=Image.new('RGB',(800,120),(20,25,40));draw=ImageDraw.Draw(sheet)
for i,(label,b) in enumerate(images):
    im=Image.new('RGB',b[2:4]);im.putdata([(v*17,)*3 if v else (20,25,40) for v in b[4]]);sheet.paste(im,(i*100,20));draw.text((i*100,0),label,fill='white')
out=ROOT/'build/graveyard533-bones';out.mkdir(exist_ok=True);sheet.save(out/'bones.png')
paths=[Path(__file__),ROOT/'build/graveyard522-enemies/report.json',ROOT/'build/graveyard519-wram/wram.bin']
(out/'report.json').write_text(json.dumps(dict(result='BONE_CANDIDATES',pairs=records,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'bones.png':digest(out/'bones.png')}),indent=2)+'\n');print(records,flush=True)
