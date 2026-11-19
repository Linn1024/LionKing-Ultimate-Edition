"""Inventory remaining native level-two actors from retained ordinary route snapshots."""
import json,struct
from collections import defaultdict
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
from PIL import Image,ImageDraw
out=ROOT/'build/cant-wait444-animals';out.mkdir(exist_ok=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
images={};exact=defaultdict(list)
for p in range(0,len(m)-40,2):
    if m[p] or m[p+1]>31:continue
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:exact[b].append(p)
seen={};records=[];paths=[Path(__file__)]
for field in (5000,6008,6504,7000,7504,8008,8504,9000,10008,11000,12008,13000):
    path=ROOT/f'build/cant-wait-native/aot/hl_wram_{field}.bin'
    if not path.exists():continue
    r=path.read_bytes();paths.append(path);w=lambda a:int.from_bytes(r[a:a+2],'little');ptr=lambda a:int.from_bytes(r[a:a+3],'little')
    work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:]=r[0x10000:]
    for draw in range(0x2000,0xffe0):
        pose=ptr(draw+10)
        if not 0xc43000<=pose<0xc4b000:continue
        actor=w(draw+4)-8
        if not 0x8000<=actor<=0xff80 or w(actor+12)!=draw:continue
        desc=ptr(actor+4);bank=(w(draw+8)>>1)&7
        if 0xc58b48<=desc<=0xc58bfc:continue
        key=(pose,bank,desc)
        if key in seen:continue
        f=snes_frame(work,pose&0x3fffff)
        if not f:continue
        b=bitmap(work,f,False,with_origin=True)
        if len(b)!=5:continue
        seen[key]=True;record=dict(field=field,native_pose=hex(pose),native_palette=bank,descriptor=hex(desc),action=hex(ptr(actor+48)),md_poses=[hex(q) for q in exact.get(b,[])],origin=b[:2],size=b[2:4]);records.append(record);images[pose]=b
sheet=Image.new('RGB',(600,max(1,(len(images)+4)//5)*180),(25,35,50));d=ImageDraw.Draw(sheet)
for i,(pose,b) in enumerate(images.items()):
    x=(i%5)*120;y=(i//5)*180;im=Image.new('RGB',b[2:4]);im.putdata([(v*17,)*3 if v else (25,35,50) for v in b[4]]);sheet.paste(im,(x,y+18));d.text((x,y),hex(pose),fill='white')
sheet.save(out/'actors.png')
(out/'report.json').write_text(json.dumps(dict(result='INVENTORIED',actors=records,scope='Remaining level-two actor/draw ownership and exact anchored art candidates; semantic classification required before runtime support.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'actors.png':digest(out/'actors.png')}),indent=2)+'\n')
print(records,flush=True)
