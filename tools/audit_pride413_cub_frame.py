"""Inspect the known unmapped cub frame; no runtime substitution is enabled."""
import json
from pathlib import Path
from pride_sprite_catalog import ROOT,read_rom,pride_snes_graphics,snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride413-cub-frame';out.mkdir(exist_ok=True)
s=pride_snes_graphics(read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native=bitmap(s,snes_frame(s,0x11372),False,with_origin=True)
def pixels(image):
    x,y,w,h,data=image
    return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
one=pixels(native);candidates=[];count=0
for at in range(0,len(m)-40,2):
    if m[at] or m[at+1]>31:continue
    frame=md_frame(m,at)
    if not frame:continue
    count+=1;image=bitmap(m,frame,True,with_origin=True)
    if len(image)!=5:continue
    two=pixels(image)
    if abs(len(two)-len(one))>160:continue
    silhouette=len(one.keys()^two.keys());indexed=sum(one.get(p,0)!=two.get(p,0) for p in one.keys()|two.keys())
    candidates.append(dict(md=hex(at),bounds=image[:4],opaque_pixels=len(two),silhouette_difference=silhouette,indexed_difference=indexed))
candidates.sort(key=lambda c:(c['indexed_difference'],c['silhouette_difference']))
paths=[Path(__file__),ROOT/'tools/pride_sprite_catalog.py']
(out/'report.json').write_text(json.dumps(dict(result='AUDITED_NO_RUNTIME_CHANGE',native_pose='C11372',native_bounds=native[:4],native_opaque_pixels=len(one),md_frame_candidates=count,nearest=candidates[:12],scope='One known native fallback cub artwork record. Static indexed/opacity comparison only; no nearest-image substitution or animation/hitbox/semantic equivalence inferred.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('native',native[:4],len(one),'MD frames',count,'nearest',candidates[:4],flush=True)
