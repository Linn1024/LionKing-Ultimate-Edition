"""Identify original vulture artwork counterparts and actual MD draw owners, read-only."""
import json,struct
from pathlib import Path
from collections import defaultdict
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard490-entry/report.json';bound(reference)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
scene=json.loads((reference.parent/'native/scene.json').read_text())
poses=sorted({p['pose'] for p in scene['pieces'] if p['actor_descriptor']==0xc58c74})
def pixels(b):
    x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
native={p:pixels(bitmap(s,snes_frame(s,p&0x3fffff),False,with_origin=True)) for p in poses}
candidates=defaultdict(list)
for q in range(0,len(m)-40,2):
    f=md_frame(m,q)
    if not f:continue
    image=bitmap(m,f,True,with_origin=True)
    if len(image)!=5:continue
    b=pixels(image)
    for p,a in native.items():
        if len(a)!=len(b) or a.keys()!=b.keys():continue
        forward=defaultdict(set);reverse=defaultdict(set)
        for k,c in a.items():forward[c].add(b[k]);reverse[b[k]].add(c)
        if max(map(len,forward.values()))==1 and max(map(len,reverse.values()))==1:
            candidates[p].append(dict(md_pose=hex(q),index_map={c:next(iter(v)) for c,v in forward.items()}))
print('PAIR_CANDIDATES',dict(candidates),flush=True)
observations=[];paths=[Path(__file__),reference]
for field in (14000,16000,18000):
    path=ROOT/f'build/md-next-levels-replay/capture-{field}/work_ram.bin';ram=path.read_bytes();paths.append(path)
    word=lambda at:struct.unpack_from('<H',ram,at&65535)[0]
    long=lambda at:word(at)<<16|word(at+2)
    possible={int(c['md_pose'],16) for cs in candidates.values() for c in cs}
    for draw in range(0x8000,0xffe8,2):
        pose=long(draw+10)
        if pose not in possible:continue
        owners=[]
        for actor in range(0x8000,0xff80,2):
            if word(actor+12)==draw and 0x8000<=word(draw+4)<0xfff8 and word(draw+4)==actor+8:
                owners.append(dict(actor=hex(actor),descriptor=hex(long(actor+4)),action=hex(long(actor)),palette=word(draw+8)>>13&3))
        observations.append(dict(field=field,draw=hex(draw),pose=hex(pose),owners=owners))
out=ROOT/'build/graveyard495-vultures';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='ART_COUNTERPARTS_INVENTORIED',native_descriptor='0xc58c74',native_pose_candidates={hex(p):cs for p,cs in candidates.items()},original_observations=observations,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('OWNERS',observations,flush=True)
