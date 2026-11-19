"""Inventory real second-level animal draws and original frame correspondences.

Read retained original RAM/VDP captures; all decoded artwork stays ignored.
This identifies renderer input, not gameplay equivalence or a finished adapter.
"""
import json,struct
from pathlib import Path
from collections import defaultdict
from PIL import Image
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait435-animals';out.mkdir(exist_ok=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
captures=sorted((ROOT/'build/cant-wait-native/aot').glob('hl_wram_*.bin'),key=lambda p:int(p.stem.split('_')[-1]))
assert captures
chosen=next(p for p in captures if int.from_bytes(p.read_bytes()[0x1ff9e:0x1ffa0],'little')==1)
ram=chosen.read_bytes();work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:0x400000]=ram[0x10000:]
md_images={};md_mask=defaultdict(list)
for p in range(0,len(m)-40,2):
    if m[p] or m[p+1]>31:continue
    f=md_frame(m,p)
    if not f:continue
    b=bitmap(m,f,True,with_origin=True)
    if len(b)!=5 or not b[4]:continue
    md_images[p]=b;md_mask[(b[2],b[3],bytes(int(v!=0) for v in b[4]))].append(p)
scene=ROOT/'build/cant-wait373/moving/scene.json';observed=json.loads(scene.read_text())
poses=sorted({p['pose']&0x3fffff for p in observed['pieces'] if p['palette']==3})
# A later real native client includes this additional animal pose.
poses.append(0x447d0)
matches=[]
for pose in poses:
    f=snes_frame(work,pose);assert f,hex(pose)
    b=bitmap(work,f,False,with_origin=True);candidates=md_mask[(b[2],b[3],bytes(int(v!=0) for v in b[4]))]
    matches.append(dict(native_pose=hex(pose),origin=b[:2],size=b[2:4],exact_mask_candidates=[dict(md_pose=hex(q),origin=md_images[q][:2],indexed_equal=b[4]==md_images[q][4]) for q in candidates]))
    # Render source indices in a neutral ramp, preserving the silhouette.
    image=Image.new('RGB',b[2:4]);image.putdata([(v*17,v*17,v*17) if v else (40,60,90) for v in b[4]])
    image.resize((b[2]*3,b[3]*3),Image.Resampling.NEAREST).save(out/(hex(pose)+'.png'))
md_live=[]
for field in (6000,8000,10000,12000):
    p=ROOT/f'build/md-next-levels-replay/capture-{field}/work_ram.bin';r=p.read_bytes()
    w=lambda a:int.from_bytes(r[a&65535:(a&65535)+2],'little')
    ptr=lambda a:(w(a)<<16|w(a+2))&0xffffff
    seen=set()
    for a in range(0x8000,0xff80,2):
        draw=w(a+12)
        if not 0x8000<=draw<=0xffe0:continue
        pose=ptr(draw+10)
        if pose not in md_images or (draw,pose) in seen:continue
        if w(draw+4)!=((a+8)&65535):continue
        seen.add((draw,pose));md_live.append(dict(field=field,actor=hex(a),descriptor=hex(ptr(a+4)),action=hex(ptr(a+48)),pose=hex(pose),palette=(w(draw+8)>>13)&3,xy=[w(a+8),w(a+10)]))
paths=[Path(__file__),chosen,scene,*[ROOT/f'build/md-next-levels-replay/capture-{n}/work_ram.bin' for n in (6000,8000,10000,12000)]]
(out/'report.json').write_text(json.dumps(dict(result='INVENTORIED',native_bank_snapshot=chosen.relative_to(ROOT).as_posix(),matches=matches,md_live=md_live,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.glob('*.png')}),indent=2)+'\n')
print('native bank',chosen.name,'matches',matches,'MD live',md_live,flush=True)
