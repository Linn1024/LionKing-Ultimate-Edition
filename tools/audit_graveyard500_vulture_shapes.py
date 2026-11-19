"""Inspect vulture sprite storage and silhouette correspondence before mapping."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
source=ROOT/'build/graveyard499-actors/report.json';actors=json.loads(source.read_text())['actors']
mdposes=sorted({int(x['pose'],16) for x in actors if 0xe7300<int(x['pose'],16)<0xe8800})
def pixels(b):
    w,h,data=b;return {(i,j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
md={q:bitmap(m,md_frame(m,q),True) for q in mdposes};records=[];images=[]
for p in (0x2b530,0x2b75e):
    f=snes_frame(s,p);b=bitmap(s,f,False);a=pixels(b)
    near=sorted((len(a.keys()^pixels(c).keys()),q) for q,c in md.items())[:3]
    records.append(dict(native_pose=hex(p|0xc00000),native_pieces=f,nearest_masks=[dict(difference=d,md_pose=hex(q)) for d,q in near]));images.append((hex(p),b))
    images.extend((hex(q),md[q]) for d,q in near)
sheet=Image.new('RGB',(800,160),(20,25,40));draw=ImageDraw.Draw(sheet)
for i,(label,b) in enumerate(images):
    im=Image.new('RGB',b[:2]);im.putdata([(v*17,)*3 if v else (20,25,40) for v in b[2]]);sheet.paste(im,(i*100,25));draw.text((i*100,0),label,fill='white')
out=ROOT/'build/graveyard500-vultures';out.mkdir(exist_ok=True);sheet.save(out/'comparison.png')
(out/'report.json').write_text(json.dumps(dict(result='STORAGE_AND_SHAPES_INVENTORIED',poses=records,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),source)},artifacts_sha256={'comparison.png':digest(out/'comparison.png')}),indent=2)+'\n');print(records,flush=True)
