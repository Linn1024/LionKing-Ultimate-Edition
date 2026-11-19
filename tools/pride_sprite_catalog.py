"""Decode original sprite frame records for first-level adapter research.

Artifacts stay local. Exact image matches establish shared art, not animation
timing, hitboxes, behavior, or complete coverage of either version.
"""
from pathlib import Path
import hashlib
import argparse
import itertools
import json
import struct
import importlib.util
from collections import Counter
from audit_scenes import ROOT,read_rom

def be16(r,p): return struct.unpack_from('>H',r,p)[0]
def le16(r,p): return struct.unpack_from('<H',r,p)[0]
def signed(n):return n-65536 if n&32768 else n

def md_frame(r,p):
    n=be16(r,p)+1
    if not 1<=n<=32:return None
    w,h=be16(r,p+6),be16(r,p+8)
    # Screen-fixed HUD frames legitimately have zero collision dimensions.
    if not 0<=w<=192 or not 0<=h<=192 or p+24+n*16>len(r):return None
    pieces=[];total=0
    for i in range(n):
        a=p+24+i*16;pw,ph,dx,dy,flags,transfer,source=struct.unpack_from('>6HI',r,a)
        if pw not in (8,16,24,32) or ph not in (8,16,24,32) or flags>>8!=((pw//8-1)<<2 | (ph//8-1)):return None
        if abs(signed(dx))>192 or abs(signed(dy))>192 or source+pw*ph//2>len(r):return None
        total+=pw*ph//2;pieces.append((signed(dx),signed(dy),pw,ph,source))
    if total!=be16(r,p+10):return None
    return pieces

def snes_frame(r,p,ram_banks=False):
    flags=le16(r,p);n=flags&127
    if not n or n>32 or p+29+n*4>len(r):return None
    w,h=le16(r,p+6),le16(r,p+8)
    if not 1<=w<=192 or not 1<=h<=192:return None
    if flags&0x8000:
        slots=n;large=(flags>>8)&63 if flags&0x4000 else slots
        source=int.from_bytes(r[p+26:p+29],'little')&0x3fffff
        if large>slots or source+slots*128>len(r):return None
        pieces=[];q=p+29
        for i in range(large):
            dx,dy=struct.unpack_from('<2H',r,q);q+=4
            if abs(signed(dx))>192 or abs(signed(dy))>192:return None
            pieces.append((signed(dx),signed(dy),16,16,source+i*64,slots*64))
        count=large*4
        if flags&0x4000:
            while q+4<=len(r) and le16(r,q)!=0xaaaa and count<slots*4:
                dx,dy=struct.unpack_from('<2H',r,q);q+=4
                if abs(signed(dx))>192 or abs(signed(dy))>192:return None
                off=count//4*64+(count%2)*32+(count%4//2)*slots*64
                pieces.append((signed(dx),signed(dy),8,8,source+off));count+=1
            if q+2>len(r) or le16(r,q)!=0xaaaa:return None
        if count*16!=le16(r,p+10):return None
        return pieces
    if (r[p+26]<0xc0 and not (ram_banks and r[p+26] in (0x7e,0x7f))) or p+27+n*6>len(r):return None
    bank=(r[p+26]&63)<<16;pieces=[]
    count=n
    if flags&0x4000:
        q=p+27+n*6
        while q+6<=len(r) and le16(r,q)!=0xaaaa and count<64:count+=1;q+=6
        if q+2>len(r) or le16(r,q)!=0xaaaa:return None
    total=0
    for i in range(count):
        a=p+27+i*6;dx,dy,source=struct.unpack_from('<3H',r,a);size=16 if i<n else 8;source|=bank
        if abs(signed(dx))>192 or abs(signed(dy))>192 or source+size*size//2>len(r):return None
        total+=size*size//4;pieces.append((signed(dx),signed(dy),size,size,source))
    if total!=le16(r,p+10):return None
    return pieces

def bitmap(r,pieces,md,order=(0,1,2,3),with_origin=False):
    pixels={}
    for piece in reversed(pieces):
        dx,dy,w,h,source=piece[:5]
        for y in range(h):
            for x in range(w):
                if md:
                    a=source+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                    v=(r[a]>>(0 if x&1 else 4))&15
                else:
                    if len(piece)==6:a=source+(x//8)*32+(y//8)*piece[5]+(y&7)*2
                    else:
                        tile=order[y//8*2+x//8] if w==16 else 0
                        a=source+tile*32+(y&7)*2
                    bit=7-(x&7)
                    v=sum(((r[a+(plane&1)+(16 if plane>=2 else 0)]>>bit)&1)<<plane for plane in range(4))
                if v:pixels[dx+x,dy+y]=v
    if not pixels:return (0,0,b'')
    x0=min(x for x,y in pixels);x1=max(x for x,y in pixels)+1;y0=min(y for x,y in pixels);y1=max(y for x,y in pixels)+1
    if x1-x0>256 or y1-y0>256:return (0,0,b'')
    image=(x1-x0,y1-y0,bytes(pixels.get((x,y),0) for y in range(y0,y1) for x in range(x0,x1)))
    return (x0,y0,*image) if with_origin else image

def pride_snes_graphics(s):
    """Reconstruct the four original level-loader WRAM graphics transfers."""
    spec=importlib.util.spec_from_file_location('tlk_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    work=bytearray(s);work.extend(bytes(0x400000-len(work)))
    for source,dest_addr in [(0xe7c514,0x7f8800),(0xe8c1a3,0x7fba00),(0xefe261,0x7fd780),(0xecf6c1,0x7fe000)]:
        data,_=lz.decompress(s,source);at=dest_addr&0x3fffff
        if at+len(data)>len(work):raise ValueError('NPC bank leaves WRAM address space')
        work[at:at+len(data)]=data
    return bytes(work)

def cub_death_pairs(s,m):
    """Explicit stream correspondences, outside the global body/art search.

    Native C089F8/C08A02 loads DFA78C into7F0000. The regular Pride NPC
    reconstruction deliberately leaves that scene-owned bank empty.
    """
    spec=importlib.util.spec_from_file_location('death_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    data,compressed=lz.decompress(s,0xdfa78c)
    work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:0x3f0000+len(data)]=data
    pairs={}
    assert int.from_bytes(m[0x7e568:0x7e56c],'big')==0x7e5b2
    for i in range(34):
        a=0xebec+i*4;b=0x7e5b2+i*4
        assert s[a]==m[b]
        p=int.from_bytes(s[a+1:a+4],'little')&0x3fffff;q=int.from_bytes(m[b+1:b+4],'big')
        if s[a]==255:
            assert i==33 and p==0xec6c and q==0x7e632
            break
        one=bitmap(work,snes_frame(work,p,True),False,with_origin=True)
        two=bitmap(m,md_frame(m,q),True,with_origin=True)
        assert one==two,('Death stream indexed art/origin differs',i,hex(p),hex(q))
        pair={'snes':hex(p),'md':[hex(q)],'origin':list(one[:2]),'size':list(one[2:4])}
        if p in pairs:assert pairs[p]==pair
        pairs[p]=pair
    assert len(pairs)==20
    return list(pairs.values()),{'source':'DFA78C','destination':'7F0000','bytes':len(data),
                                'compressed_bytes':compressed,'sha256':hashlib.sha256(data).hexdigest()}

def adult_source_pairs(md_rom):
    """Reviewed shared adult/body source links; keep generic regeneration complete."""
    spec=json.loads((ROOT/'tools/adult_sprite_pairs.json').read_text())
    rows=[]
    for pair in spec['pairs']:
        q=int(pair['md'],16);frame=md_frame(md_rom,q)
        if not frame:raise ValueError('Reviewed adult MD source is not drawable')
        x,y,w,h,_=bitmap(md_rom,frame,True,with_origin=True)
        rows.append(dict(snes=pair['snes'],md=[hex(q)],origin=[x,y],size=[w,h],extra_pixels=pair.get('extra_pixels',[])))
    return rows

def cub_source_pairs(snes_rom,md_rom):
    """Complete reviewed cub drawings, including pixels outside native OAM pieces."""
    spec=json.loads((ROOT/'tools/cub_sprite_pairs.json').read_text());rows=[]
    for pair in spec['pairs']:
        p=int(pair['snes'],16);q=int(pair['md'],16)
        native=snes_frame(snes_rom,p);external=md_frame(md_rom,q)
        if not native or not external:raise ValueError('Reviewed cub source is not drawable')
        bx,by,w,h,pixels=bitmap(md_rom,external,True,with_origin=True);extra=[]
        for j in range(h):
            for i in range(w):
                c=pixels[j*w+i]
                if c and not any(x<=bx+i<x+ww and y<=by+j<y+hh for x,y,ww,hh,*_ in native):
                    extra.append([bx+i,by+j,c])
        if len(extra)>64:raise ValueError('Reviewed cub source leaves more than64 native-piece pixels')
        rows.append(dict(snes=hex(p),md=[hex(q)],origin=[bx,by],size=[w,h],extra_pixels=extra))
    return rows

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--header',type=Path)
    ap.add_argument('--out',type=Path,default=ROOT/'build/pride-sprites');args=ap.parse_args()
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    dest=args.out;dest.mkdir(parents=True,exist_ok=True)
    original_size=len(s)
    # First-level NPC graphics are decompressed into WRAM, not read directly
    # from ROM. Recipes are confirmed by the original decompressor trace.
    s=pride_snes_graphics(s)
    md={};snes={}
    # Frame records are mixed with code/data. Structural constraints, byte counts
    # and source bounds eliminate ordinary words; candidates still need context.
    for p in range(0,len(m)-40,2):
        if m[p] or m[p+1]>31:continue
        f=md_frame(m,p)
        if f:md[p]=f
    native=snes_frame(s,0x11d5b)
    md_images={};
    for p,f in md.items():
        image=bitmap(m,f,True)
        if image[2]:md_images.setdefault(image,[]).append(p)
    for order in itertools.permutations(range(4)):
        image=bitmap(s,native,False,order)
        matches=md_images.get(image,[])
        if matches: print('native tile order',order,'idle pose exact matches',[hex(x) for x in matches],flush=True)
    # Use the conventional row-major order for the initial catalog. The report
    # retains only verified exact matches; no nearest-pose substitution.
    order=(0,1,2,3)
    for p in range(original_size-40):
        if s[p]>127:continue
        f=snes_frame(s,p)
        if f:snes[p]=f
    matches=[];near=[]
    for p,f in snes.items():
        image=bitmap(s,f,False,order)
        if image in md_images:matches.append({'snes':hex(p),'md':[hex(x) for x in md_images[image]],'size':list(image[:2])})
    def sparse(image):
        x,y,w,h,data=image
        return {((y+j+256)*512+x+i+256)*16+c for j in range(h) for i in range(w) if (c:=data[j*w+i])}
    md_sparse={};by_count={}
    for p,f in md.items():
        image=bitmap(m,f,True,with_origin=True)
        if len(image)!=5 or not image[4]:continue
        points=sparse(image);md_sparse[p]=(points,image)
        by_count.setdefault(len(points),[]).append(p)
    exact={int(x['snes'],16) for x in matches}
    for p,f in snes.items():
        if p in exact:continue
        image=bitmap(s,f,False,order,True)
        if len(image)!=5:continue
        points=sparse(image);candidates=[]
        for n in range(max(0,len(points)-4),len(points)+5):
            for q in by_count.get(n,[]):
                difference=len(points^md_sparse[q][0])
                candidates.append((difference,q))
        candidates.sort()
        if not candidates or candidates[0][0]>8:continue
        difference,q=candidates[0];best=md_sparse[q][0]
        # Duplicate records with identical artwork are fine. A close competing
        # pose with different art makes the automatic pairing ambiguous.
        runner=next((d for d,other in candidates if md_sparse[other][0]!=best),100000)
        if runner<=max(40,difference*10):continue
        x,y,w,h,data=md_sparse[q][1];original={v//16:v%16 for v in points};extra=[]
        for v in sorted(best):
            position,c=divmod(v,16)
            if original.get(position,0)!=c:extra.append([position%512-256,position//512-256,c])
        if len(extra)>8:continue
        identical=[other for _,other in candidates if md_sparse[other][0]==best]
        near.append({'snes':hex(p),'md':[hex(other) for other in identical],'size':[w,h],'origin':[x,y],
                     'different_indexed_points':difference,'next_distinct_pose_difference':runner,'extra_pixels':extra})
    death,death_bank=cub_death_pairs(s,m)
    adult=adult_source_pairs(m)+cub_source_pairs(s,m)
    report={'scope':'structurally valid frame candidates; exact art matches only; semantic/animation validation still required',
            'snes_candidates':len(snes),'md_candidates':len(md),'exact_matches':matches,'pixel_art_variants':near,
            'cub_death_frames':death,'cub_death_graphics_bank':death_bank,'adult_frames':adult}
    (dest/'catalog.json').write_text(json.dumps(report,indent=2)+'\n')
    # Explicit, reviewed semantic correspondences stay as address metadata.
    # Re-read artwork from the verified ROMs; never store extracted pixels.
    npc_pairs=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
    npcs={}
    for pair in npc_pairs:
        p=int(pair['snes'],16)&0x3fffff;q=int(pair['md'],16)
        if p not in snes or q not in md:raise ValueError('NPC pair is not a valid frame')
        a=bitmap(s,snes[p],False,with_origin=True);b=bitmap(m,md[q],True,with_origin=True)
        def pixels(im):
            x,y,w,h,data=im
            return {(x+i,y+j):data[j*w+i] for j in range(h) for i in range(w) if data[j*w+i]}
        apix,bpix=pixels(a),pixels(b)
        if pair['role']=='lizard':
            # Shared lizard silhouettes have different frame origins. Compare
            # corresponding art pixels, not their shifted world coordinates.
            apix={(x-a[0],y-a[1]):c for (x,y),c in apix.items()}
            bpix={(x-b[0],y-b[1]):c for (x,y),c in bpix.items()}
        if pair['role']=='leaves' and a!=b:raise ValueError('Leaf art/origin correspondence changed')
        if 'anchored_mask_difference' in pair and len(apix.keys()^bpix.keys())!=pair['anchored_mask_difference']:
            raise ValueError('Reviewed NPC anchored silhouette correspondence changed')
        native_offset={0:0x7b93,2:0x2fac7,4:0x2fb07,6:0x7d53,7:0x2fb67}[pair['native_palette']]
        native_colors=[le16(s,native_offset+i*2) for i in range(16)]
        palette_offset=int.from_bytes(m[0x1cfdb4+44:0x1cfdb4+48],'big')+pair['md_palette']*32
        def color(c):
            values=[((c>>shift)&7)*4+(((c>>shift)&7)>>2) for shift in (1,5,9)]
            return values[0]|values[1]<<5|values[2]<<10
        md_colors=[color(be16(m,palette_offset+i*2)) for i in range(16)]
        def distance(c,d):return sum(weight*(((c>>shift)&31)-((d>>shift)&31))**2 for shift,weight in [(0,3),(5,6),(10,2)])
        def remap(source,target,source_colors,target_colors):
            values=[0]
            for c in range(1,16):
                counts=Counter(target[xy] for xy,v in source.items() if v==c and xy in target)
                values.append(counts.most_common(1)[0][0] if counts else min(range(1,16),key=lambda d:distance(source_colors[c],target_colors[d])))
            return values
        token=pair['role']=='continue_token'
        if token and not (a[0]==b[0] and a[1]==b[1]+1 and a[2:]==b[2:]):
            raise ValueError('Continue token indexed art or one-row original origin changed')
        npcs[p]={'snes':hex(p),'md':[hex(q)],'origin':b[:2],'size':b[2:4],
                 'role':{'hyena':1,'lizard':2,'porcupine':3,'pickup':4,'leaves':5,'defeat_puff':6,'pickup_popup':7,'continue_token':8}[pair['role']],
                 'native_palette':pair['native_palette'],'md_palette':pair['md_palette'],
                 'md_to_native':list(range(16)) if token else remap(bpix,apix,md_colors,native_colors),
                 'native_to_md':list(range(16)) if token else remap(apix,bpix,native_colors,md_colors)}
    from cw_sprite_catalog import append_rhinos,append_hippos,append_ride_obstacles,append_giraffes
    append_rhinos(s,m,snes,md,npcs)
    append_hippos(s,m,snes,md,npcs)
    append_ride_obstacles(s,m,snes,md,npcs)
    append_giraffes(s,m,snes,md,npcs)
    from graveyard_sprite_catalog import append_vultures,append_skull_hyenas,append_bone_structures,append_pillar_atlas
    append_vultures(s,m,snes,md,npcs)
    append_skull_hyenas(s,m,snes,md,npcs)
    append_bone_structures(s,m,snes,md,npcs)
    append_pillar_atlas(s,m,npcs)
    from next_scene_catalog import append_next_scenes
    append_next_scenes(s,m,snes,md,npcs)
    from hakuna_sprite_catalog import append_hakuna_gorilla,append_hakuna_destiny_actors
    append_hakuna_gorilla(s,m,snes,md,npcs)
    append_hakuna_destiny_actors(s,m,snes,md,npcs)
    from later_sprite_catalog import append_later_actors
    append_later_actors(s,m,snes,md,npcs)
    if args.header:
        text=['/* Generated from the verified local ROM pair. Do not commit. */',
              'static const struct SpriteMap { unsigned snes,md; int x,y,w,h; unsigned extra_count; TlkMdSpriteExtra extra[64]; unsigned role,native_palette,md_palette; unsigned char md_to_native[16],native_to_md[16]; } sprite_map[] = {']
        combined={int(x['snes'],16):x for x in matches+near};combined.update(npcs)
        for pair in adult:
            key=int(pair['snes'],16)
            if key in combined and pair['md'][0] not in combined[key]['md']:raise ValueError('Adult source conflicts with another mapping')
            combined[key]=pair
        for pair in death:
            key=int(pair['snes'],16)
            assert key not in combined,'Death metadata must stay separate from ordinary body mappings'
            combined[key]=pair
        for match in sorted(combined.values(),key=lambda x:int(x['snes'],16)):
            p=int(match['snes'],16)
            if 'origin' in match:x,y=match['origin'];w,h=match['size']
            else:x,y,w,h,pixels=bitmap(s,snes[p],False,order,True)
            extra=match.get('extra_pixels',[]);values=','.join('{'+','.join(map(str,pixel))+'}' for pixel in extra) or '{0,0,0}'
            suffix=''
            if 'role' in match:
                suffix=','+','.join(str(match[k]) for k in ('role','native_palette','md_palette'))
                suffix+=', {'+','.join(map(str,match['md_to_native']))+'}, {'+','.join(map(str,match['native_to_md']))+'}'
            text.append(f'{{0x{p:x}, {match["md"][0]}, {x}, {y}, {w}, {h}, {len(extra)}, {{{values}}}{suffix}}},')
        text.append('};\n')
        text.append('static const unsigned cub_death_poses[] = {'+','.join(pair['snes'] for pair in death)+'};\n')
        args.header.parent.mkdir(parents=True,exist_ok=True)
        content='\n'.join(text)
        if not args.header.exists() or args.header.read_text()!=content:args.header.write_text(content)
    print('SNES',len(snes),'MD',len(md),'exact',len(matches),'unambiguous small art variants',len(near),'semantic NPC pairs',len(npcs))

if __name__=='__main__':main()
