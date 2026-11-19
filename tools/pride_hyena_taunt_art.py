"""Review the paired original hyena taunt streams; never auto-enable matches."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.tools/pythonlibs'))
from PIL import Image,ImageDraw
from pride_sprite_catalog import ROOT,read_rom,pride_snes_graphics,snes_frame,md_frame,bitmap

PAIRS=[(0xc2adf8,0xb61c4),(0xc2ae57,0xb624c),(0xc2aeaa,0xb62d4),
       (0xc2aefd,0xb636c),(0xc2af4c,0xb63d4),(0xc2afb7,0xb646c),
       (0xc2b02a,0xb6514),(0xc2b085,0xb658c)]


def main():
    s=pride_snes_graphics(read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    def points(im):
        x,y,w,h,data=im
        return {(x+i,y+j) for j in range(h) for i in range(w) if data[j*w+i]}
    old=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
    addresses={int(row['md'],16) for row in old if row['role']=='hyena'}|{md for _,md in PAIRS}
    images={p:bitmap(m,md_frame(m,p),True,with_origin=True) for p in addresses}
    sheet=Image.new('RGB',(700,len(PAIRS)*110),(30,30,33));draw=ImageDraw.Draw(sheet)
    rows=[]
    for index,(native,md) in enumerate(PAIRS):
        im=bitmap(s,snes_frame(s,native&0x3fffff),False,with_origin=True)
        candidates=sorted((len(points(im)^points(image)),p) for p,image in images.items())
        rows.append({'snes':hex(native),'expected_md':hex(md),'native_origin':im[:2],
                     'md_origin':images[md][:2], 'nearest':[{'md':hex(p),'mask_difference':d} for d,p in candidates[:4]]})
        for column,(label,image) in enumerate([(hex(native),im)]+[(f'{p:x} d={d}',images[p]) for d,p in candidates[:3]]):
            draw.text((column*175,index*110),label,fill='white')
            x,y,w,h,data=image
            pic=Image.new('RGB',(w,h));pix=pic.load()
            for yy in range(h):
                for xx in range(w):
                    value=data[yy*w+xx];pix[xx,yy]=(value*16,)*3 if value else (30,30,33)
            sheet.paste(pic,(column*175,index*110+17))
    out=ROOT/'build/hyena-taunt-art';out.mkdir(exist_ok=True)
    sheet.save(out/'review.png');(out/'review.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
