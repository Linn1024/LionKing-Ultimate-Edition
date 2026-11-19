"""Append reviewed gorilla action-phase metadata; no extracted images are tracked."""
import json
from audit_scenes import ROOT
def append_hakuna_gorilla(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap
    for pair in json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        assert p not in npcs and q in md,(hex(p),hex(q))
        b=bitmap(m,md[q],True,with_origin=True);assert len(b)==5
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=13,native_palette=6,md_palette=3,native_to_md=pair['native_to_md'],md_to_native=pair['md_to_native'])

def append_hakuna_destiny_actors(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap
    for pair in json.loads((ROOT/'tools/hakuna_destiny_actor_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        assert p not in npcs and q in md,(hex(p),hex(q))
        b=bitmap(m,md[q],True,with_origin=True);assert len(b)==5
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],**{k:pair[k] for k in ('role','native_palette','md_palette','native_to_md','md_to_native')})
    append_hakuna_coconuts(s,m,snes,md,npcs)
    append_hakuna_platform_caps(s,m,snes,md,npcs)
    append_shared_life_and_hakuna_effect(s,m,snes,md,npcs)


def append_hakuna_coconuts(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap
    for pair in json.loads((ROOT/'tools/hakuna_coconut_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16);q=int(pair['md'],16)
        assert p not in npcs and q in md
        b=bitmap(m,md[q],True,with_origin=True)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],**{k:pair[k]for k in ('role','native_palette','md_palette','native_to_md','md_to_native')})


def append_hakuna_platform_caps(s,m,snes,md,npcs):
    """Original paired factories; native tile sources are scene-owned WRAM."""
    from pride_sprite_catalog import bitmap,md_frame
    for pair in json.loads((ROOT/'tools/hakuna_platform_cap_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16);q=int(pair['md'],16)
        assert p not in npcs
        b=bitmap(m,md_frame(m,q),True,with_origin=True)
        assert list(b[:2])==pair['origin']and list(b[2:4])==pair['size']
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],**{k:pair[k]for k in ('role','native_palette','md_palette','native_to_md','md_to_native')})


def append_shared_life_and_hakuna_effect(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap,md_frame
    for pair in json.loads((ROOT/'tools/world_life_and_hakuna_effect_pairs.json').read_text())['pairs']:
        p=int(pair['snes'],16);q=int(pair['md'],16)
        b=bitmap(m,md_frame(m,q),True,with_origin=True)
        assert list(b[:2])==pair['origin']and list(b[2:4])==pair['size']
        row=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],**{k:pair[k]for k in ('role','native_palette','md_palette','native_to_md','md_to_native')})
        if p in npcs:
            assert all(npcs[p][k]==row[k]for k in ('role','native_palette','md_palette','native_to_md','md_to_native'))
        npcs[p]=row
