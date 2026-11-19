"""Append original Graveyard vulture animation artwork to prepared sprite metadata."""
import json
from collections import Counter
from audit_scenes import ROOT

def append_pillar_atlas(s,m,npcs):
    """Eight factory DMA phases, not ordinary ROM frame records; source4992."""
    import hashlib,struct
    from pride_sprite_catalog import bitmap,le16,be16
    keys=struct.unpack_from('<8H',s,0x1ccd2)
    native_colors=[le16(s,0x2f707+i*2) for i in range(16)]
    palette=int.from_bytes(m[0x1cfdb4+2*48+44:0x1cfdb4+2*48+48],'big')+32
    def color(c):
        v=[((c>>shift)&7)*4+(((c>>shift)&7)>>2)for shift in (1,5,9)]
        return v[0]|v[1]<<5|v[2]<<10
    external_colors=[color(be16(m,palette+i*2))for i in range(16)]
    def distance(a,b):return sum(w*(((a>>sh)&31)-((b>>sh)&31))**2 for sh,w in ((0,3),(5,6),(10,2)))
    hashes=[]
    for phase,key in enumerate(keys):
        p=0x10000+key;q=0x922f4+phase*8
        assert p not in npcs and s[p+26]==0xc4
        sources=[le16(s,p+31+j*6)|0x40000 for j in range(8)]
        assert sources==[0x49853+phase*512+j*128 for j in range(4)]+[0x4a853+phase*512+j*128 for j in range(4)]
        first,tail=struct.unpack_from('>2I',m,q)
        assert (first,tail)==(0x9009c+phase*512,0x9109c+phase*512)
        coords=[(-16,0),(0,0),(-16,16),(0,16),(-16,32),(0,32),(-16,48),(0,48)]
        a=bitmap(s,[(dx,dy,16,16,src)for (dx,dy),src in zip(coords,sources)],False,with_origin=True)
        b=bitmap(m,[(-16,0,32,16,first),(-16,16,32,16,first+256),(-16,32,32,16,tail),(-16,48,32,16,tail+256)],True,with_origin=True)
        def points(im):
            x,y,w,h,data=im
            return {(x+i,y+j):data[j*w+i]for j in range(h)for i in range(w)if data[j*w+i]}
        aa,bb=points(a),points(b)
        def mapping(source,target,sc,tc):
            votes={c:Counter()for c in range(1,16)}
            for xy in source.keys()&target.keys():votes[source[xy]][target[xy]]+=1
            return [0]+[votes[c].most_common(1)[0][0]if votes[c]else min(range(1,16),key=lambda d:distance(sc[c],tc[d]))for c in range(1,16)]
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=[-16,0],size=[32,64],role=29,native_palette=4,md_palette=1,
                     native_to_md=mapping(aa,bb,native_colors,external_colors),md_to_native=mapping(bb,aa,external_colors,native_colors))
        piece_hashes=[]
        for src in sources:
            image=bitmap(s,[(0,0,16,16,src)],False,with_origin=True)
            xx,yy,ww,hh,data=image;fnv=2166136261
            for y in range(16):
                for x in range(16):
                    c=data[(y-yy)*ww+x-xx]if xx<=x<xx+ww and yy<=y<yy+hh else 0
                    fnv=((fnv^c)*16777619)&0xffffffff
            piece_hashes.append(fnv)
        hashes.append(piece_hashes)
    text='/* Reviewed original factory DMA identities; no artwork payload. Source4992. */\n'
    text+='static const unsigned graveyard_pillar_keys[8]={'+','.join(hex(0x10000+k)for k in keys)+'};\n'
    text+='static const unsigned graveyard_pillar_piece_hashes[8][8]={'+','.join('{'+','.join(hex(h)+'u'for h in row)+'}'for row in hashes)+'};\n'
    sha=hashlib.sha256(struct.pack('<15H',*native_colors[1:])).digest()
    text+='static const unsigned char graveyard_pillar_palette_hash[32]={'+','.join(hex(c)for c in sha)+'};\n'
    text+='static inline int TlkGraveyardPillarIndex(unsigned key){key&=0x3fffff;for(unsigned i=0;i<8;i++)if(key==graveyard_pillar_keys[i])return (int)i;return -1;}\n'
    header=ROOT/'engine/runner/tlk_graveyard_pillar_metadata.h'
    if not header.exists()or header.read_text()!=text:header.write_text(text)

def append_bone_structures(s,m,snes,md,npcs):
    """Original marker-owned structures; mixed index maps have live RAM proof."""
    from pride_sprite_catalog import bitmap
    spec=json.loads((ROOT/'tools/graveyard_bone_object_pairs.json').read_text())
    for pair in spec['pairs']:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        assert p not in npcs and q in md
        b=bitmap(m,md[q],True,with_origin=True)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],
            **{key:pair[key] for key in ('role','native_palette','md_palette','native_to_md','md_to_native')})

def append_skull_hyenas(s,m,snes,md,npcs):
    """Pair the distinct socket stream C256E3/MD7F1A2, not fighting poses.

    Both streams blink repeatedly, then reveal 9 successive head/body phases.
    Native art lives in scene WRAM; shared hyena color indices are derived from
    the reviewed ordinary body pairs, without treating Pride WRAM as socket art.
    """
    from pride_sprite_catalog import bitmap,le16,be16
    native=(0x1301,0x133c,0x1377,0x13b2,0x13ed,0x1428,0x1463,0x149a,0x14d1,0x1508,0x1557)
    external=(0x8b226,0x8b28e,0x8b2f6,0x8b34e,0x8b3a6,0x8b3fe,0x8b446,0x8b48e,0x8b4e6,0x8b51e,0x8b586)
    votes={c:Counter() for c in range(1,16)};back={c:Counter() for c in range(1,16)}
    def points(b):
        x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
    for p,pair in list(npcs.items()):
        if pair['role']!=1:continue
        a=points(bitmap(s,snes[p],False,with_origin=True));b=points(bitmap(m,md[int(pair['md'][0],16)],True,with_origin=True))
        for xy in a.keys()&b.keys():votes[a[xy]][b[xy]]+=1;back[b[xy]][a[xy]]+=1
    native_colors=[le16(s,0x7d53+i*2) for i in range(16)]
    palette=int.from_bytes(m[0x1cfdb4+44:0x1cfdb4+48],'big')+96
    def color(c):
        v=[((c>>shift)&7)*4+(((c>>shift)&7)>>2) for shift in (1,5,9)];return v[0]|v[1]<<5|v[2]<<10
    external_colors=[color(be16(m,palette+i*2)) for i in range(16)]
    def distance(a,b):return sum(weight*(((a>>shift)&31)-((b>>shift)&31))**2 for shift,weight in ((0,3),(5,6),(10,2)))
    forward=[0]+[votes[c].most_common(1)[0][0] if votes[c] else min(range(1,16),key=lambda d:distance(native_colors[c],external_colors[d])) for c in range(1,16)]
    reverse=[0]+[back[c].most_common(1)[0][0] if back[c] else min(range(1,16),key=lambda d:distance(external_colors[c],native_colors[d])) for c in range(1,16)]
    for p,q in zip(native,external):
        assert p not in npcs and q in md
        b=bitmap(m,md[q],True,with_origin=True)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=1,native_palette=6,md_palette=3,native_to_md=forward,md_to_native=reverse)

def append_vultures(s,m,snes,md,npcs):
    from pride_sprite_catalog import bitmap,snes_frame,be16,le16
    spec=json.loads((ROOT/'tools/graveyard_vulture_pairs.json').read_text())
    # Whole-color correspondence comes from ordinary static flight drawings.
    # Later native phases can use work-memory graphics; no Pride bank is used
    # as supposed native vulture pixels during preparation.
    forward={c:Counter() for c in range(1,16)};reverse={c:Counter() for c in range(1,16)}
    def points(b):
        x,y,w,h,data=b;return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
    for p,q in spec['pairs']:
        p=int(p,16)&0x3fffff;q=int(q,16)
        if not 0x3f014<=p<=0x3f335:continue
        a=points(bitmap(s,snes_frame(s,p),False,with_origin=True));b=points(bitmap(m,md[q],True,with_origin=True))
        for k in a.keys()&b.keys():forward[a[k]][b[k]]+=1;reverse[b[k]][a[k]]+=1
    native=[le16(s,0x2f727+i*2) for i in range(16)]
    def color(c):
        values=[((c>>shift)&7)*4+(((c>>shift)&7)>>2) for shift in (1,5,9)];return values[0]|values[1]<<5|values[2]<<10
    palette=int.from_bytes(m[0x1cfdb4+2*48+44:0x1cfdb4+2*48+48],'big')+96
    external=[color(be16(m,palette+i*2)) for i in range(16)]
    def distance(c,d):return sum(weight*(((c>>shift)&31)-((d>>shift)&31))**2 for shift,weight in ((0,3),(5,6),(10,2)))
    def mapping(votes,source,target):return [0]+[votes[c].most_common(1)[0][0] if votes[c] else min(range(1,16),key=lambda d:distance(source[c],target[d])) for c in range(1,16)]
    n_to_m=mapping(forward,native,external);m_to_n=mapping(reverse,external,native)
    for native_pose,md_pose in spec['pairs']:
        p=int(native_pose,16)&0x3fffff;q=int(md_pose,16);assert snes_frame(s,p) and q in md and p not in npcs
        b=bitmap(m,md[q],True,with_origin=True)
        npcs[p]=dict(snes=hex(p),md=[hex(q)],origin=b[:2],size=b[2:4],role=10,native_palette=5,md_palette=3,native_to_md=n_to_m,md_to_native=m_to_n)
