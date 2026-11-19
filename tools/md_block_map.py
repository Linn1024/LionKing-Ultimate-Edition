"""Measure exact art matches between the two versions' block dictionaries."""
from pathlib import Path
import struct
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tlk_lz',ROOT/'engine/tools/re/decompress.py')
lz=importlib.util.module_from_spec(spec); spec.loader.exec_module(lz)

def measure(level):
    snes=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    md=(ROOT/'Lion King, The (World).md').read_bytes()
    rec=int.from_bytes(snes[0x357+level*3:0x35a+level*3],'little')&0x3fffff
    gfx,_=lz.decompress(snes,int.from_bytes(snes[rec+6:rec+9],'little'))
    cells,_=lz.decompress(snes,int.from_bytes(snes[rec+9:rec+12],'little'))
    blocks=int.from_bytes(snes[rec+15:rec+18],'little')&0x3fffff
    mgfx=(ROOT/f'build/md-assets/l{level+1:02}-tiles.bin').read_bytes()
    mcells=(ROOT/f'build/md-assets/l{level+1:02}-map.bin').read_bytes()
    mblocks=struct.unpack_from('>I',md,0x1cfdb4+level*48+20)[0]
    used=set(x&0xfff8 for x in struct.unpack('<'+str(len(cells)//2)+'H',cells))
    mused=set(x&0xfff8 for x in struct.unpack('>'+str(len(mcells)//2)+'H',mcells))
    def shape(off,is_md):
        rom=md if is_md else snes; base=mblocks if is_md else blocks; tiles=mgfx if is_md else gfx
        words=struct.unpack_from(('>' if is_md else '<')+'4H',rom,base+off)
        result=bytearray()
        for y in range(16):
            for x in range(16):
                w=words[y//8*2+x//8]; px=x&7; py=y&7
                if w&(0x800 if is_md else 0x4000): px=7-px
                if w&(0x1000 if is_md else 0x8000): py=7-py
                t=(w&(0x7ff if is_md else 0x3ff))*32
                if is_md: color=(tiles[t+py*4+px//2]>>(0 if px&1 else 4))&15 if t+32<=len(tiles) else 0
                else: color=sum(((tiles[t+py*2+(p&1)+(16 if p>=2 else 0)]>>(7-px))&1)<<p for p in range(4)) if t+32<=len(tiles) else 0
                result.append(color)
        return bytes(result)
    candidates={shape(i,True):i for i in mused}
    matched={i:candidates.get(shape(i,False)) for i in used}
    mapped=sum(matched[i&0xfff8] is not None for i in struct.unpack('<'+str(len(cells)//2)+'H',cells))
    print('level',level,'unique',sum(v is not None for v in matched.values()),'/',len(used),'map cells',mapped,'/',len(cells)//2)

if __name__=='__main__':
    for l in (0,1,2,4,5,6,7,8,9): measure(l)
