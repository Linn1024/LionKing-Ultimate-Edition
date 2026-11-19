"""Append reviewed second-level graphics metadata to the existing prepared sprite map."""
import json
from collections import Counter
from audit_scenes import ROOT


def append_giraffes(s,m,snes,md,npcs):
    """Original descriptor and bend/return streams identify all seven images."""
    from pride_sprite_catalog import bitmap,le16,be16
    pairs=((0x7d93,0xce15a),(0x7de6,0xce1c2),(0x7e35,0xce23a),(0x7e78,0xce2b2),
           (0x7ebf,0xce30a),(0x7f12,0xce372),(0x7f59,0xce3da))
    nc=[le16(s,0x50b9a+i*2)for i in range(16)]
    def color(v):
        return sum((((v>>a)&7)*4+(((v>>a)&7)>>2))<<b for a,b in ((1,0),(5,5),(9,10)))
    mc=[color(be16(m,0x1ea624+i*2))for i in range(16)]
    def pixels(im):
        x,y,w,h,data=im;return{(x+i,y+j):data[j*w+i]for j in range(h)for i in range(w)if data[j*w+i]}
    def remap(a,b,ca,cb):
        result=[0]
        for c in range(1,16):
            votes=Counter(b[k]for k,v in a.items()if v==c and k in b)
            result.append(votes.most_common(1)[0][0]if votes else min(range(1,16),key=lambda j:sum(w*(((ca[c]>>bit)&31)-((cb[j]>>bit)&31))**2 for bit,w in ((0,3),(5,6),(10,2)))))
        return result
    for p,q in pairs:
        assert p in snes and q in md and p not in npcs
        a=bitmap(s,snes[p],False,with_origin=True);b=bitmap(m,md[q],True,with_origin=True)
        assert a[:4]==b[:4];ap,bp=pixels(a),pixels(b)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=27,
            native_palette=5,md_palette=1,md_to_native=remap(bp,ap,mc,nc),native_to_md=remap(ap,bp,nc,mc))


def append_ride_obstacles(s,m,snes,md,npcs):
    """Constructor-proven MD images; no dependency on a live native RAM bank.

    The native pictures use low-WRAM graphics, outside the generic Pride bank.
    Mixed artwork/palette sources use nearest colors from the original palettes;
    MD artwork+MD palette always uses exact original indices and colors.
    """
    from pride_sprite_catalog import bitmap,le16,be16
    pairs=((0xc45a16,0xd10a2,2),(0xc3b6f7,0xcdffa,1),(0xc3b756,0xce072,0),
           (0xc3b77b,0xce09a,1),(0xc3b7f2,0xce132,0))
    def color(v):
        return sum((((v>>a)&7)*4+(((v>>a)&7)>>2))<<b for a,b in ((1,0),(5,5),(9,10)))
    def remap(a,b):
        return [0]+[min(range(1,16),key=lambda j:sum(w*(((c>>bit)&31)-((b[j]>>bit)&31))**2
                    for bit,w in ((0,3),(5,6),(10,2))))for c in a[1:]]
    for native,external,bank in pairs:
        p=native&0x3fffff;assert p not in npcs and external in md
        b=bitmap(m,md[external],True,with_origin=True)
        na=0x50b7a+bank*32 if bank else 0x7b93
        ma=0x1ea604+bank*32 if bank else 0x1d78aa
        nc=[le16(s,na+i*2)for i in range(16)];mc=[color(be16(m,ma+i*2))for i in range(16)]
        npcs[p]=dict(snes=hex(p),md=[hex(external)],origin=b[:2],size=b[2:4],
            role=26,native_palette=bank,md_palette=bank,
            md_to_native=remap(mc,nc),native_to_md=remap(nc,mc))


def append_hippos(s,m,snes,md,npcs):
    """Original hippo scripts pair animation states; local anchors differ."""
    from pride_sprite_catalog import bitmap,le16,be16
    spec=json.loads((ROOT/'tools/cw_hippo_pairs.json').read_text())
    native_colors=[le16(s,0x60375+i*2)for i in range(16)]
    def color(c):
        v=[((c>>shift)&7)*4+(((c>>shift)&7)>>2)for shift in (1,5,9)]
        return v[0]|v[1]<<5|v[2]<<10
    md_colors=[color(be16(m,0x1ea624+i*2))for i in range(16)]
    for native,external in spec['pairs']:
        p=int(native,16)&0x3fffff;q=int(external,16)
        assert p in snes and q in md and p not in npcs
        a=bitmap(s,snes[p],False,with_origin=True);b=bitmap(m,md[q],True,with_origin=True)
        # Compare matching local image positions after removing their different
        # authored anchors. Unused colors use the original palette distance.
        def remap(src,dst,ca,cb):
            answer=[0]
            for c in range(1,16):
                votes=Counter(dst[4][y*dst[2]+x]for y in range(min(src[3],dst[3]))for x in range(min(src[2],dst[2]))if src[4][y*src[2]+x]==c and dst[4][y*dst[2]+x])
                answer.append(votes.most_common(1)[0][0]if votes else min(range(1,16),key=lambda n:sum((((ca[c]>>shift)&31)-((cb[n]>>shift)&31))**2 for shift in (0,5,10))))
            return answer
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=24,native_palette=6,md_palette=1,
                     md_to_native=remap(b,a,md_colors,native_colors),native_to_md=remap(a,b,native_colors,md_colors))

def append_rhinos(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap,le16,be16
    spec=json.loads((ROOT/'tools/cw_rhino_pairs.json').read_text())
    native_prefix=[0xc3cb64,0xc3cbbf,0xc3cc2e,0xc3cca1,0xc3cd08,0xc3cd6b,0xc3cdd2,0xc3ce35]
    md_prefix=[0xd0e32,0xd0eda,0xd0f92,0xd101a]
    for start,poses,rom,endian,duration in ((0x26df2,native_prefix,s,'little',1),(0xb8d5e,md_prefix,m,'big',3)):
        for i,pose in enumerate(poses):assert rom[start+i*4]==duration and int.from_bytes(rom[start+i*4+1:start+i*4+4],endian)==pose
    # Original MD descriptor uses palette1, and points at the reviewed head frame.
    assert m[0xb8d3c:0xb8d46]==bytes.fromhex('0019cc3c2002000d0a82')
    native_colors=[le16(s,0x50b9a+i*2) for i in range(16)]
    def color(c):
        v=[((c>>shift)&7)*4+(((c>>shift)&7)>>2) for shift in (1,5,9)]
        return v[0]|v[1]<<5|v[2]<<10
    md_colors=[color(be16(m,0x1ea604+32+i*2)) for i in range(16)]
    def pixels(b):
        x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
    def remap(a,b,ca,cb):
        result=[0]
        for c in range(1,16):
            votes=Counter(b[k] for k,v in a.items() if v==c and k in b)
            result.append(votes.most_common(1)[0][0] if votes else min(range(1,16),key=lambda n:sum((((ca[c]>>shift)&31)-((cb[n]>>shift)&31))**2 for shift in (0,5,10))))
        return result
    for native,external in spec['pairs']:
        p=int(native,16)&0x3fffff;q=int(external,16)
        assert p in snes and q in md and p not in npcs
        a=bitmap(s,snes[p],False,with_origin=True);b=bitmap(m,md[q],True,with_origin=True)
        ap,bp=pixels(a),pixels(b)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=9,native_palette=5,md_palette=1,md_to_native=remap(bp,ap,md_colors,native_colors),native_to_md=remap(ap,bp,native_colors,md_colors))
