"""Independent default composition against original art and default CPU palettes.

Original default SAT binds death latency and visible revival art separately;
normal-play transfer has its own phase. Native colors retain all five bits.
"""
import array
import struct
from audit_scenes import ROOT
from probe_pride_scene_render import art_file,rgb,rows


def verify_default_pixels(folder, width, frames_md, palettes_md, expected_count, authentic_gpu=True):
    original=ROOT/'build/pride-death-controller/original-palettes.csv'
    scalar={}
    for r in rows(original):
        if r['case']!='9':continue
        age=int(r['age']);cub=int(r['index'])<16
        source=int(r['next_color'] if age>=274 else r['death_color']);actual=int(r['actual'])
        for shift in (0,3,6):
            key=(age,cub,(source>>shift)&7);value=(actual>>shift)&7
            assert key not in scalar or scalar[key]==value
            scalar[key]=value
    def fade(c, age, cub, md):
        age=min(age,300)
        out=0
        for shift in (0,5,10):
            v=(c>>shift)&31
            if md:
                q=v//4;assert v==q*4+q//4, (age,c,shift)
                q=scalar[age,cub,q];v=q*4+q//4
            elif age>=274:v=min(v,4*((age-274)//3))
            else:
                losses=0 if cub and age<225 else (age-225+2)//3 if cub else (age+2)//3 if age<24 else 8
                v=max(0,v-4*losses)
            out|=v<<shift
        return rgb(out)
    death=art_file(ROOT/'build/pride-owned-death-art/original-bitmaps.bin',b'TLKDART1')
    revival=art_file(ROOT/'build/pride-owned-revival-art/original-bitmaps.bin',b'TLKRART1')
    poses={int(r['age']):int(r['snes_pose']) for r in rows(ROOT/'build/pride-death-controller/original-fields.csv') if r['case']=='9'}
    poses.update({int(r['age']):int(r['snes_pose']) for r in rows(ROOT/'build/pride-revival-scene/original-revival.csv') if r['case']=='8'})
    mdrom=(ROOT/'Lion King, The (World).md').read_bytes()
    mdpalette=[]
    for i in range(16):
        raw=int.from_bytes(mdrom[0x1d78aa+i*2:0x1d78ac+i*2],'big')
        mdpalette.append(sum((((raw>>s)&7)*4+((raw>>s)&7)//4)<<d for s,d in ((1,0),(5,5),(9,10))))
    count=width*224;compared=0;ages=[];first_xy=None;observed_md=False;observed_snes=False;previous_record=None;duplicates=0
    with (folder/'render-owned.rgb').open('rb') as f:
        assert f.read(8)==b'PRDRGB01' and struct.unpack('<II',f.read(8))==(width,224)
        while header:=f.read(24):
            age,pose,x,y,flip,md=struct.unpack('<IIiiII',header)
            repeated=bool(ages and age==ages[-1])
            assert age==(ages[-1] if repeated else len(ages)) and md==palettes_md
            palette=struct.unpack('<16H',f.read(32))
            full=array.array('I');full.frombytes(f.read(count*4))
            tags=array.array('I');tags.frombytes(f.read(count*4))
            actual=array.array('I');actual.frombytes(f.read(count*4))
            assert len(full)==len(tags)==len(actual)==count
            record=(header,palette,full.tobytes(),tags.tobytes(),actual.tobytes())
            if repeated:assert record==previous_record;duplicates+=1
            previous_record=record
            assert all((tag&0xffffff) in (0,0x00ff00,0xff0000) and tag>>24<=1 for tag in tags)
            observed_md|=any((t&0xffffff)==0xff0000 for t in tags);observed_snes|=any((t&0xffffff)==0x00ff00 for t in tags)
            lut={}
            for c,t in set(zip(full,tags)):
                color=(c>>19)&31 | ((c>>11)&31)<<5 | ((c>>3)&31)<<10
                lut[c,t]=fade(color,age,False,(t&0xffffff)==0xff0000)
            expected=array.array('I',(lut[c,t] for c,t in zip(full,tags)))
            if (age<249 or age>=274) and not(authentic_gpu and age==0):
                source_age=min(age,300)
                if authentic_gpu:
                    source_age=min(max(age-(1 if age<=24 else 2),0),224) if age<249 else min(max(274,age-2),300)
                assert pose==poses[source_age],(age,hex(pose),hex(poses[source_age]))
                bx,by,w,h,a,b=(death if age<249 else revival)[pose]
                if age<249:
                    if first_xy is None:first_xy=x,y
                    moves=max(0,min(201,age-(25 if authentic_gpu else 23)))
                    def toward(start,target):return start+max(-moves,min(moves,target-start))
                    assert (x,y)==(toward(first_xy[0],width//2),toward(first_xy[1],128)),(age,x,y)
                selected=mdpalette if md else palette
                colors=[fade(c,age,age<249,bool(md)) for c in selected]
                indexes=b if frames_md else a
                for py in range(h):
                    for px in range(w):
                        index=indexes[py*w+px]
                        dx=x+(-bx-px-1 if flip else bx+px);dy=y+by+py
                        if index and 0<=dx<width and 0<=dy<224 and not(tags[dy*width+dx]&0x01000000):expected[dy*width+dx]=colors[index]
            elif authentic_gpu and age==0:assert pose==0
            else:assert pose==0 and not any(actual)
            if expected!=actual:
                bad=next(i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b)
                raise AssertionError((age,bad%width,bad//width,hex(expected[bad]),hex(actual[bad]),hex(full[bad]),hex(tags[bad])))
            if age==274:assert not any(actual),'Health publication must still be black'
            compared+=count
            if not repeated:ages.append(age)
    assert len(ages)==expected_count
    return dict(owned_fields=len(ages),duplicate_presentation_records=duplicates,pixels_compared=compared,md_base_palette_observed=observed_md,
                snes_base_palette_observed=observed_snes,black_reload_and_restore_verified=274 in ages)

