"""Check sampled original final-menu pictures against their actual VDP layers."""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels
from pride_sprite_catalog import md_frame


LEVELS=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]


def main():
    base=ROOT/'build/pride-final-menu-art-original';source=base/'report.json';data=bound(source)
    out=ROOT/'build/pride-final-menu-art-audit';out.mkdir();checks={};rows={}
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    for case,observations in data['observations'].items():
        records=[]
        for age in (118,120,124,125,140,141,160,180,200,220):
            folder=base/case/str(age);vram=(folder/'vram.bin').read_bytes()
            regs=(folder/'reg.bin').read_bytes();vs=(folder/'vsram.bin').read_bytes()
            cram=struct.unpack('<64H',(folder/'cram.bin').read_bytes())
            word=lambda b,a:struct.unpack_from('<H',b,a%len(b))[0]
            def tile_pixel(tile,x,y):
                if tile&0x800:x=7-x
                if tile&0x1000:y=7-y
                p=vram[(((tile&2047)*32+y*4+x//2)&65535)^1]
                return (p>>(0 if x&1 else 4))&15
            def rgb(index):
                c=cram[index];return tuple(LEVELS[i][c>>(i*3)&7] for i in range(3))
            # Retain the actual scene's plane dimensions/scroll initialization.
            cols=[32,64,32,128][regs[16]&3];heights=[32,64,96,128][regs[16]>>4&3]
            opaque=[];scroll=[]
            for plane,table in enumerate(((regs[2]&56)<<10,(regs[4]&7)<<13)):
                hs=word(vram,(regs[13]&63)<<10|plane*2)&1023;vertical=word(vs,plane*2)&1023
                count=0
                for y in range(224):
                    for x in range(320):
                        px=(x-hs)%(cols*8);py=(y+vertical)%(heights*8)
                        tile=word(vram,table+(py//8*cols+px//8)*2)
                        count+=bool(tile_pixel(tile,px&7,py&7))
                opaque.append(count);scroll.append([hs,vertical])
            row=next(r for r in observations if r['age']==age)
            picture=[rgb(regs[7]&63)]*(320*224)
            for sprite in reversed(row['sprites']):
                ypos,size,attr,xpos=sprite['words'];w=((size>>10&3)+1)*8;h=((size>>8&3)+1)*8
                left=(xpos&511)-128;top=(ypos&511)-128
                for y in range(h):
                    for x in range(w):
                        dx=left+x;dy=top+y
                        if not (0<=dx<320 and 0<=dy<224):continue
                        sx=w-1-x if attr&0x800 else x;sy=h-1-y if attr&0x1000 else y
                        tile=(attr&2047)+(sx//8)*(h//8)+sy//8
                        c=tile_pixel(tile,sx&7,sy&7)
                        if c:picture[dy*320+dx]=rgb((attr>>13&3)*16+c)
            actual=pixels(folder/'window.png');different=sum(p!=q for p,q in zip(picture,actual[2]))
            checks[case+str(age)+'_sprite_picture']=not different and actual[:2]==(320,224)
            checks[case+str(age)+'_transparent_planes']=opaque==[0,0]
            checks[case+str(age)+'_simple_raster']=not (regs[11]&7 or regs[12]&14 or regs[17] or regs[18])
            records.append(dict(age=age,opaque_plane_pixels=opaque,scroll=scroll,
                sprite_count=len(row['sprites']),differing_pixels=different))
        rows[case]=records
    # Identify live frame-record pointers without treating stale RAM as ownership.
    candidates={}
    for case in rows:
        ram=(base/case/'120/work_ram.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
        found={}
        for at in range(0x8000,0xfffc,2):
            address=(word(at)<<16|word(at+2))&0xffffff
            if 0x1000<=address<len(rom)-536:
                pieces=md_frame(rom,address)
                if pieces:found.setdefault(hex(address),[]).append(hex(at))
        candidates[case]=found
    paths=[Path(__file__),source,ROOT/'tools/pride_sprite_catalog.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,rows=rows,
        frame_pointer_candidates_not_ownership_proof=candidates,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
