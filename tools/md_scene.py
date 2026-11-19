"""Render decoded MD scenery against a live reference capture (local only)."""
from pathlib import Path
import struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
rom=(ROOT/'Lion King, The (World).md').read_bytes()

def main():
    assets=ROOT/'build/md-assets'
    cells=(assets/'l01-map.bin').read_bytes()
    background=(assets/'l01-background.bin').read_bytes()
    tiles=(assets/'l01-tiles.bin').read_bytes()
    blocks=0x283d8e
    colors=struct.unpack_from('>64H',rom,0x28e45c)
    def rgb(c):
        # The reference core's RGB565 expansion, without analogue filtering.
        r=((c>>1)&7)*2; g=((c>>5)&7)*2; b=((c>>9)&7)*2
        return (((r*2+(r>>3))*255//31),((g*4+(g>>2))*255//63),((b*2+(b>>3))*255//31))
    palette=[rgb(c) for c in colors]
    def pixel(word,x,y):
        if word&0x800: x=7-x
        if word&0x1000: y=7-y
        off=(word&0x7ff)*32+y*4+x//2
        if off>=len(tiles): return None
        p=(tiles[off]>>(0 if x&1 else 4))&15
        return palette[((word>>13)&3)*16+p] if p else None
    ram=(ROOT/'build/md-lab/work_ram.bin').read_bytes()
    cx,cy=struct.unpack_from('<HH',ram,0x880c)
    image=Image.new('RGB',(320,224)); px=image.load()
    for y in range(224):
        for x in range(320):
            wx=cx+x; wy=cy+y
            bx=(cx*38//256+x)%512; by=(cy*20//256+y)%(len(background)//128*8)
            bw=struct.unpack_from('>H',background,(by//8*64+bx//8)*2)[0]
            c=pixel(bw,bx&7,by&7) or palette[0]
            if 0<=wx<1600 and 0<=wy<1280:
                block=struct.unpack_from('>H',cells,(wy//16*100+wx//16)*2)[0]&0xfff8
                word=struct.unpack_from('>H',rom,blocks+block+(wy%16//8*2+wx%16//8)*2)[0]
                c=pixel(word,wx&7,wy&7) or c
            px[x,y]=c
    image.save(ROOT/'build/md-scene.png')
    reference=Image.open(ROOT/'build/md-lab/screen.png').convert('RGB')
    error=sum(a!=b for a,b in zip(image.getdata(),reference.getdata()))
    print('differing pixels (sprites/HUD included):',error,'of',320*224)

if __name__=='__main__': main()
