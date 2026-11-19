"""Contact sheet of original pickup candidates, with source palette colours."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PIL import Image,ImageDraw
from pride_sprite_catalog import ROOT,read_rom,snes_frame,md_frame,bitmap,be16,le16

def main():
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    def snes_color(c):return tuple(((c>>shift)&31)*255//31 for shift in (0,5,10))
    def md_color(c):return tuple(((c>>shift)&7)*34 for shift in (1,5,9))
    sp=[snes_color(le16(s,0x7b93+c*2)) for c in range(16)]
    mp=[md_color(be16(m,0x1d78aa+c*2)) for c in range(16)]
    entries=[]
    for p in (0x5287a,0x5289b,0x528bc,0x528dd,0x529ed):
        entries.append((f'SNES {p|0xc00000:x}',bitmap(s,snes_frame(s,p),False,with_origin=True),sp))
    for p in range(0x94000,0x95200,2):
        f=md_frame(m,p)
        if f:entries.append((f'MD {p:x}',bitmap(m,f,True,with_origin=True),mp))
    sheet=Image.new('RGB',(800,((len(entries)+7)//8)*112),(32,32,35));draw=ImageDraw.Draw(sheet)
    for index,(label,im,palette) in enumerate(entries):
        if len(im)!=5:continue
        col,row=index%8,index//8;draw.text((col*100,row*112),label,fill='white')
        x,y,w,h,data=im;picture=Image.new('RGB',(w,h));picture.putdata([palette[c] if c else (32,32,35) for c in data])
        sheet.paste(picture.resize((w*3,h*3),Image.Resampling.NEAREST),(col*100,row*112+20))
    dest=ROOT/'build/pride-sprites/pickup-candidates.png';sheet.save(dest);print(dest,len(entries),'candidates')

if __name__=='__main__':main()
