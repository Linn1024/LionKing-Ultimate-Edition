"""Compare the actual Pride caption's native glyphs with original MD SAT pixels.

Displayed-region evidence only: this does not establish MD actor ownership or
enable a title renderer. All ROM-derived pixels stay in ignored build/.
"""
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.tools/pythonlibs'))
from PIL import Image,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_sprite_catalog import bitmap


def main():
    out=ROOT/'build/pride-title-art-review2';out.mkdir()
    snes_path=ROOT/'Lion King, The (USA).sfc';rom=snes_path.read_bytes()
    ram_path=ROOT/'build/native-pickup-flight/hl_wram_1000.bin';ram=ram_path.read_bytes()
    p=0x17dd;count=struct.unpack_from('<H',ram,p)[0]&127
    assert count==13 and ram[p+26]==0xe8
    native=[];records=[]
    for i in range(count):
        x,y,source=struct.unpack_from('<3H',ram,p+27+i*6)
        frame=bitmap(rom,[(0,0,16,16,(ram[p+26]&63)<<16|source)],False,with_origin=True)
        native.append(frame);records.append(dict(x=x,y=y,source=hex(0xe80000|source)))
    captured=ROOT/'build/pride-intro-reference/capture-1320'
    vram_path=captured/'vram.bin';reg_path=captured/'reg.bin'
    vram=vram_path.read_bytes();reg=reg_path.read_bytes()
    word=lambda a:struct.unpack_from('<H',vram,a)[0]
    base=(reg[5]&0x7e)<<9;seen=set();slot=0;points={};sprites=[]
    while slot not in seen:
        seen.add(slot);at=base+slot*8;size=word(at+2);attr=word(at+4)
        x=(word(at+6)&511)-128;y=(word(at)&511)-128
        w=(((size>>10)&3)+1)*8;h=(((size>>8)&3)+1)*8
        # Bounded displayed caption region from the inspected screenshot.
        # Include pieces one pixel below the baseline: the first region-only
        # attempt wrongly dropped the A by assuming that piece was a bug.
        # This spatial selection still does not prove semantic actor ownership.
        if 72<=y<=80 and 59<=x<=251:
            assert not attr&0x1800
            sprites.append(dict(slot=slot,x=x,y=y,width=w,height=h,attributes=attr))
            for dy in range(h):
                for dx in range(w):
                    a=(((attr&2047)+(dx//8)*(h//8)+dy//8)*32+(dy&7)*4+(dx&7)//2)&65535
                    c=vram[a^1]>>(0 if dx&1 else 4)&15
                    if c:points[x+dx,y+dy]=c
        slot=size&127
        if not slot:break
    assert sprites and points
    matches=[]
    for index,(ox,oy,w,h,data) in enumerate(native):
        candidates=[];mask_candidates=[]
        for y in range(72,89-h):
            for x in range(55,269-w):
                actual=bytes(points.get((x+i%w,y+i//w),0) for i in range(w*h))
                if actual==data:candidates.append([x,y])
                if all(bool(a)==bool(b) for a,b in zip(actual,data)):mask_candidates.append([x,y])
        matches.append(dict(letter='THEPRIDELANDS'[index],native_record=records[index],
                            native_origin_size=[ox,oy,w,h],exact_indexed_matches=candidates,
                            exact_silhouette_matches=mask_candidates))
    sheet=Image.new('RGB',(640,140),(28,28,32));draw=ImageDraw.Draw(sheet)
    colors=[(28,28,32)]+[(min(255,i*17),min(255,i*14),0) for i in range(1,16)]
    for column in (0,1):
        draw.text((column*320+6,6),'SNES glyphs at native spacing' if column==0 else 'Original MD caption SAT region',fill='white')
        image=Image.new('RGB',(256,40),(28,28,32))
        if column:
            for (x,y),c in points.items():image.putpixel((x-40,y-64),colors[c])
        else:
            for rec,(ox,oy,w,h,data) in zip(records,native):
                for i,c in enumerate(data):
                    if c:image.putpixel((rec['x']+ox+i%w,8+oy+i//w),colors[c])
        sheet.paste(image,(column*320+6,36))
    sheet.save(out/'glyphs.png')
    paths=[Path(__file__),snes_path,ram_path,vram_path,reg_path,
           ROOT/'build/pride-intro-reference/report.json',ROOT/'build/pride-intro-windows/commands.json']
    result=dict(result='CAPTION_GLYPHS_COMPARED',native_glyphs=count,md_display_region_sprites=sprites,
        glyph_matches=matches,semantic_owner_verified=False,production_title_source_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={'glyphs.png':digest(out/'glyphs.png')})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],[(r['letter'],len(r['exact_indexed_matches']),len(r['exact_silhouette_matches'])) for r in matches],flush=True)


if __name__=='__main__':main()
