"""Find literal shared vulture silhouettes without assuming equal color indices or origins."""
import json
from pathlib import Path
from collections import defaultdict
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap,pride_snes_graphics
from build_pride_compiled_hooks import digest
s0=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');s=pride_snes_graphics(s0)
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
def pixels(b):
    x,y,w,h,data=b;return {(i,j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
md={};masks=defaultdict(list)
for q in range(0xe7300,0xe8800,2):
    f=md_frame(m,q)
    if not f:continue
    b=bitmap(m,f,True,with_origin=True)
    if len(b)!=5:continue
    md[q]=b;masks[frozenset(pixels(b))].append(q)
pairs=[];candidates=0
for p in range(len(s0)-40):
    if s[p]>127:continue
    f=snes_frame(s,p)
    if not f:continue
    b=bitmap(s,f,False,with_origin=True)
    if len(b)!=5:continue
    candidates+=1;a=pixels(b)
    for q in masks.get(frozenset(a),[]):
        z=pixels(md[q]);forward=defaultdict(set);reverse=defaultdict(set)
        for k,c in a.items():forward[c].add(z[k]);reverse[z[k]].add(c)
        if max(map(len,forward.values()))==1 and max(map(len,reverse.values()))==1:
            pairs.append(dict(native_pose=hex(p|0xc00000),md_pose=hex(q),native_origin=b[:2],md_origin=md[q][:2],index_map={c:next(iter(v)) for c,v in forward.items()}))
out=ROOT/'build/graveyard518-vulture-pairs';out.mkdir(exist_ok=True)
paths=[Path(__file__),ROOT/'tools/pride_sprite_catalog.py',ROOT/'build/graveyard499-actors/report.json']
(out/'report.json').write_text(json.dumps(dict(result='SHARED_SILHOUETTE_INVENTORY',native_candidates=candidates,md_candidates=len(md),pairs=pairs,scope='Read-only literal silhouette/color-permutation search, using original ROM plus existing Pride WRAM reconstruction. Any other RAM-backed native bank remains unqualified. No nearest-image mapping or runtime implementation.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('CANDIDATES',candidates,len(md),'PAIRS',pairs,flush=True)
