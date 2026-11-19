"""Reviewed late-scene static actor links; addresses/color maps only are tracked."""
import json
from audit_scenes import ROOT
def append_later_actors(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap
    for pair in [pair for name in ('later_actor_pairs.json','pride_actor_pairs.json','bonus_actor_pairs.json') for pair in json.loads((ROOT/'tools'/name).read_text())['pairs']]:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        # Context-only aliases are image keys, never native ROM frame addresses.
        if 0x3e1000<=p<=0x3e1007: assert pair["role"]==19
        if p in npcs and pair["role"]==4 and npcs[p].get("role")==4:continue
        assert p not in npcs and q in md,(hex(p),hex(q))
        x,y,w,h,_=bitmap(m,md[q],True,with_origin=True)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=[x,y],size=[w,h],**{k:pair[k] for k in ('role','native_palette','md_palette','native_to_md','md_to_native')})
