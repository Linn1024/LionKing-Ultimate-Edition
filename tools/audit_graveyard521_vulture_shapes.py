"""Locate candidate native vulture animation families by whole silhouette, for visual review only."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
s0=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');s=bytearray(s0);s.extend(bytes(0x400000-len(s)));s[0x3e0000:]=(ROOT/'build/graveyard519-wram/wram.bin').read_bytes()
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
def mask(b):
    x,y,w,h,data=b;result=0
    for j in range(h):
        for i in range(w):
            if data[j*w+i]:result|=1<<(j*256+i)
    return result
native={};md={}
for p in range(len(s0)-40):
    if s[p]>127:continue
    f=snes_frame(s,p)
    if not f:continue
    b=bitmap(s,f,False,with_origin=True)
    if len(b)==5:native[p]=(mask(b),b)
for q in range(0xe7300,0xe8800,2):
    f=md_frame(m,q)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:md[q]=(mask(b),b)
records=[];images=[]
for q,(alpha,b) in md.items():
    near=sorted(((alpha^v[0]).bit_count(),p) for p,v in native.items())[:3]
    records.append(dict(md_pose=hex(q),candidates=[dict(native_pose=hex(p|0xc00000),mask_difference=d,native_origin=native[p][1][:2],md_origin=b[:2]) for d,p in near]))
    images.append((hex(q),b));images.append((hex(near[0][1]),native[near[0][1]][1]))
sheet=Image.new('RGB',(800,((len(images)+7)//8)*115),(20,25,40));draw=ImageDraw.Draw(sheet)
for i,(label,b) in enumerate(images):
    x=i%8*100;y=i//8*115;im=Image.new('RGB',b[2:4]);im.putdata([(v*17,)*3 if v else (20,25,40) for v in b[4]]);sheet.paste(im,(x,y+20));draw.text((x,y),label,fill='white')
out=ROOT/'build/graveyard521-vultures';out.mkdir(exist_ok=True);sheet.save(out/'comparison.png')
paths=[Path(__file__),ROOT/'build/graveyard519-wram/report.json',ROOT/'build/graveyard519-wram/wram.bin']
(out/'report.json').write_text(json.dumps(dict(result='CANDIDATES_FOR_VISUAL_REVIEW',scope=__doc__+' No mapping/ownership/timing claim follows from nearest silhouettes.',pairs=records,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'comparison.png':digest(out/'comparison.png')}),indent=2)+'\n');print([(x['md_pose'],x['candidates'][0]) for x in records],flush=True)
