"""Inventory live original Graveyard actor drawings before assigning enemy roles."""
import json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import md_frame,bitmap
from build_pride_compiled_hooks import digest
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
out=ROOT/'build/graveyard497-actors';out.mkdir(exist_ok=True);records=[];images={};paths=[Path(__file__)]
for field in (14000,16000,18000):
    path=ROOT/f'build/md-next-levels-replay/capture-{field}/work_ram.bin';ram=path.read_bytes();paths.append(path)
    word=lambda at:struct.unpack_from('<H',ram,at&65535)[0]
    long=lambda at:word(at)<<16|word(at+2)
    for actor in range(0x8000,0xff80,2):
        draw=word(actor+12)
        if not 0x8000<=draw<0xffe8 or word(draw+4)!=actor+8:continue
        pose=long(draw+10)
        if pose>=len(m)-40:continue
        f=md_frame(m,pose)
        if not f:continue
        b=bitmap(m,f,True,with_origin=True)
        if len(b)!=5:continue
        images[pose]=b;records.append(dict(field=field,actor=hex(actor),descriptor=hex(long(actor+4)),action=hex(long(actor)),pose=hex(pose),palette=word(draw+8)>>13&3,position=[word(actor+8),word(actor+10)]))
sheet=Image.new('RGB',(800,((len(images)+7)//8)*110),(20,25,40));d=ImageDraw.Draw(sheet)
for i,(pose,b) in enumerate(sorted(images.items())):
    x=i%8*100;y=i//8*110;im=Image.new('RGB',b[2:4]);im.putdata([(v*17,)*3 if v else (20,25,40) for v in b[4]]);sheet.paste(im,(x,y+20));d.text((x,y),hex(pose),fill='white')
sheet.save(out/'actors.png')
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_ACTOR_INVENTORY',actors=records,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'actors.png':digest(out/'actors.png')}),indent=2)+'\n')
print(records,flush=True)
