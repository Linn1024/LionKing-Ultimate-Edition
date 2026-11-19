"""Inspect the MD level records and shared Westwood LZ/RLE assets."""
from pathlib import Path
import importlib.util
import struct

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tlk_lz',ROOT/'engine/tools/re/decompress.py')
lz=importlib.util.module_from_spec(spec); spec.loader.exec_module(lz)
def main():
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    out=ROOT/'build/md-assets'; out.mkdir(parents=True,exist_ok=True)
    for level in range(14):
        rec=0x1cfdb4+level*48
        width,height=struct.unpack_from('>HH',rom,rec+12)
        print('level',level+1,'size',width,height)
        for name,field in [('map',16),('background',24),('tiles',28)]:
            ptr=struct.unpack_from('>I',rom,rec+field)[0]
            try:
                data,used=lz.decompress(rom,ptr)
                print(' ',name,hex(ptr),len(data),'bytes',used,'compressed')
                (out/f'l{level+1:02d}-{name}.bin').write_bytes(data)
            except Exception as e: print(name,'ERROR',e)
    vram=(ROOT/'build/md-lab/vram.bin').read_bytes()
    gfx=(out/'l01-tiles.bin').read_bytes()
    print('tile blob first64',gfx[:64].hex())
    for n in range(0,min(len(gfx),32768),32):
        if len(set(gfx[n:n+32]))>4:
            part=gfx[n:n+32]
            swapped=b''.join(part[i:i+2][::-1] for i in range(0,32,2))
            print('gfx',hex(n),'matches VRAM',vram.find(part),vram.find(swapped))
            if n>400: break
    print('camera MD x,y',struct.unpack_from('<HH',(ROOT/'build/md-lab/work_ram.bin').read_bytes(),0x880c))

if __name__=='__main__': main()
