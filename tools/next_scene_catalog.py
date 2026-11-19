"""Append reviewed fourth/fifth-level sprite frames to the prepared catalog."""
import json
from audit_scenes import ROOT
def append_next_scenes(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap
    for pair in json.loads((ROOT/'tools/next_scene_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        assert q in md and p not in npcs,(hex(p),hex(q))
        b=bitmap(m,md[q],True,with_origin=True);assert len(b)==5
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=pair['role'],native_palette=pair['native_palette'],md_palette=pair['md_palette'],native_to_md=pair['native_to_md'],md_to_native=pair['md_to_native'])
