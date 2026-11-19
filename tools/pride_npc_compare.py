"""Visual research sheet for unmatched NPC poses; similarity never enables an adapter."""
import json
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PIL import Image,ImageDraw
from pride_sprite_catalog import ROOT,read_rom,pride_snes_graphics,snes_frame,md_frame,bitmap

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--palette',type=int,default=6);args=ap.parse_args()
    s=pride_snes_graphics(read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    def points(image):
        x,y,w,h,data=image
        return {(x+i,y+j) for j in range(h) for i in range(w) if data[j*w+i]}
    candidates=[]
    for p in range(0,len(m)-40,2):
        if m[p] or m[p+1]>31:continue
        f=md_frame(m,p)
        if not f:continue
        image=bitmap(m,f,True,with_origin=True)
        if len(image)==5:candidates.append((p,image,points(image)))
    rows=[]
    for item in json.loads((ROOT/'build/pride-sprites/npc-catalog.json').read_text()):
        if item['palette']!=args.palette:continue
        p=int(item['snes'],16);f=snes_frame(s,p&0x3fffff)
        if not f:continue
        image=bitmap(s,f,False,with_origin=True);native=points(image)
        rank=sorted((len(native^pts),q,im) for q,im,pts in candidates if abs(len(native)-len(pts))<max(150,len(native)//3))
        rows.append((p,image,rank[:3]))
    sheet=Image.new('RGB',(600,len(rows)*96),(32,32,35));draw=ImageDraw.Draw(sheet);report=[]
    for row,(p,native,matches) in enumerate(rows):
        report.append({'snes':hex(p),'candidates':[{'md':hex(q),'mask_difference':d} for d,q,im in matches]})
        for col,(label,im) in enumerate([(hex(p),native)]+[(f'{q:x} d={d}',im) for d,q,im in matches]):
            draw.text((col*150,row*96),label,fill='white');x,y,w,h,data=im
            pic=Image.new('RGB',(w,h));pix=pic.load()
            for yy in range(h):
                for xx in range(w):
                    c=data[yy*w+xx];pix[xx,yy]=(c*16,)*3 if c else (32,32,35)
            sheet.paste(pic,(col*150,row*96+16))
    dest=ROOT/'build/pride-sprites';stem=f'npc-nearest-{args.palette}'
    sheet.save(dest/(stem+'.png'));(dest/(stem+'.json')).write_text(json.dumps(report,indent=2))
    print('wrote',len(rows),'comparison rows for palette',args.palette)

if __name__=='__main__':main()
