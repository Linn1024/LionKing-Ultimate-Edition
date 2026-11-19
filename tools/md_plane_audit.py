"""Inspect captured MD VDP planes; raw previews omit sprites, window and blending.

Uses a standard tools/md_lab.py capture. This is evidence from one frame, not
an assertion that all levels have the same semantic layers or raster effects.
"""
from pathlib import Path
import argparse
import json
import struct

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('capture',type=Path)
    args=ap.parse_args(); dest=args.capture
    regs=(dest/'reg.bin').read_bytes(); vram=(dest/'vram.bin').read_bytes()
    vs=(dest/'vsram.bin').read_bytes(); cram=struct.unpack('<64H',(dest/'cram.bin').read_bytes())
    if regs[11]&4 or regs[12]&6: raise ValueError('column V-scroll/interlace require a different preview decoder')
    width=320 if regs[12]&1 else 256; height=240 if regs[1]&8 else 224
    cols=[32,64,32,128][regs[16]&3]; rows=[32,64,96,128][(regs[16]>>4)&3]
    hbase=(regs[13]&63)<<10; hmask=[0,7,248,255][regs[11]&3]
    table=[(regs[2]&56)<<10,(regs[4]&7)<<13]
    def word(data,at): return struct.unpack_from('<H',data,at%len(data))[0]
    results=[]
    for plane in range(2):
        pixels=bytearray(); opaque=0; high=0; scrolls=set(); palette_counts=[0]*4
        for y in range(height):
            hs=word(vram,hbase+(y&hmask)*4+plane*2)&1023
            vertical=word(vs,plane*2)&1023; scrolls.add((hs,vertical))
            for x in range(width):
                px=(x-hs)%(cols*8); py=(y+vertical)%(rows*8)
                tile=word(vram,table[plane]+(py//8*cols+px//8)*2)
                xx=px&7; yy=py&7
                if tile&0x800: xx=7-xx
                if tile&0x1000: yy=7-yy
                # Exported VRAM bytes are word-swapped on this little-endian core.
                packed=vram[(((tile&2047)*32+yy*4+xx//2)&65535)^1]
                color=(packed>>(0 if xx&1 else 4))&15; bank=(tile>>13)&3
                if color: opaque+=1; palette_counts[bank]+=1; high+=bool(tile&0x8000)
                c=cram[bank*16+color] if color else 0
                # The exported core CRAM is internal RGB9, not raw 0x0EEE CRAM.
                pixels.extend((((c>>s)&7)*34 for s in (0,3,6)))
        (dest/f'plane-{chr(65+plane)}.ppm').write_bytes(f'P6\n{width} {height}\n255\n'.encode()+pixels)
        results.append({'plane':chr(65+plane),'name_table':hex(table[plane]),'opaque_pixels_before_composition':opaque,
                        'high_priority_opaque_pixels':high,'palette_pixels':palette_counts,'scroll_pairs':sorted(scrolls)})
    report={'scope':'single-frame raw planes, no sprites/window/priority composition/shadow-highlight; not a count of logical layers',
            'native_size':[width,height],'map_size':[cols*8,rows*8],
            'hscroll_mode':regs[11]&3,'vscroll_per_column':bool(regs[11]&4),
            'window_registers':[regs[17],regs[18]],'window_name_table':hex((regs[3]&60)<<10),
            'planes':results}
    (dest/'planes.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))

if __name__=='__main__': main()
