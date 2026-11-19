"""Check the default installed menu package with the decoder-free reader.

ROM/captured banks here are independent research oracles, never reader inputs.
Run with 32-bit Python and pass the installed package and a fresh output folder.
"""
import ctypes as C
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from audit_pride_final_menu_ram import menu_frame


def main():
    package=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir();record=package.read_bytes()
    count=struct.unpack_from('<I',record,20)[0];frames=[];at=240
    for i in range(count):
        frame,x,y,w,h=struct.unpack_from('<5I',record,at);frames.append(frame);at+=20+w*h
    source=ROOT/'build/pride-final-menu-art-original/report.json';original=bound(source)
    reader_path=ROOT/'build/pride-final-art-installed/reader.dll';dll=C.CDLL(str(reader_path))
    dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
    dll.TlkFinalArtFree.argtypes=[C.c_void_p]
    dll.TlkFinalArtBounds.argtypes=[C.c_void_p,C.c_uint32,*([C.POINTER(C.c_int)]*4)]
    dll.TlkFinalArtPixel.argtypes=[C.c_void_p,C.c_uint32,C.c_int,C.c_int]
    buffer=C.create_string_buffer(record);art=dll.TlkFinalArtLoad(buffer,len(record));assert art
    C.memset(buffer,0,len(record))
    rom=(ROOT/'Lion King, The (World).md').read_bytes();metadata={f:menu_frame(rom,f) for f in frames}
    bank=(source.parent/'continue/120/work_ram.bin').read_bytes();bank=bytes(bank[i^1] for i in range(len(bank)))
    def pixels(pointer,w,h):
        data=bank if pointer>=0xff0000 else rom;offset=pointer&65535 if pointer>=0xff0000 else pointer
        return bytes(data[offset+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2]>>(0 if x&1 else 4)&15
            for y in range(h) for x in range(w))
    checks={};compared=0
    try:
        for frame,pieces in metadata.items():
            assert pieces
            left=min(p[0] for p in pieces);top=min(p[1] for p in pieces)
            right=max(p[0]+p[2] for p in pieces);bottom=max(p[1]+p[3] for p in pieces)
            expected=[0]*((right-left)*(bottom-top))
            for x,y,w,h,pointer in reversed(pieces):
                raw=pixels(pointer,w,h)
                for dy in range(h):
                    for dx in range(w):
                        c=raw[dy*w+dx]
                        if c:expected[(y-top+dy)*(right-left)+x-left+dx]=c
            values=[C.c_int() for _ in range(4)];ok=dll.TlkFinalArtBounds(art,frame,*map(C.byref,values))
            checks[hex(frame)+'_original_bounds']=bool(ok) and [v.value for v in values]==[left,top,right-left,bottom-top]
            actual=[dll.TlkFinalArtPixel(art,frame,x,y) for y in range(top,bottom) for x in range(left,right)]
            checks[hex(frame)+'_original_image']=actual==expected;compared+=len(actual)
        for case,observations in original['observations'].items():
            for age in (118,120,124,125,140,141,160,180,200,220):
                folder=source.parent/case/str(age);vram=(folder/'vram.bin').read_bytes()
                row=next(r for r in observations if r['age']==age);sprites=[]
                for entry in row['sprites']:
                    y,size,attr,x=entry['words'];w=((size>>10&3)+1)*8;h=((size>>8&3)+1)*8
                    raw=bytes(vram[((((attr&2047)*32+i)&65535)^1)] for i in range(w*h//2))
                    sprites.append((entry['index'],(x&511)-128,(y&511)-128,w,h,raw))
                covered=set()
                for pieces in metadata.values():
                    anchors=None
                    for x,y,w,h,pointer in pieces:
                        data=bank if pointer>=0xff0000 else rom;offset=pointer&65535 if pointer>=0xff0000 else pointer
                        raw=data[offset:offset+w*h//2]
                        candidates={(sx-x,sy-y) for i,sx,sy,sw,sh,sraw in sprites if (sw,sh,sraw)==(w,h,raw)}
                        anchors=candidates if anchors is None else anchors&candidates
                        if not anchors:break
                    for ax,ay in anchors or ():
                        for x,y,w,h,pointer in pieces:
                            data=bank if pointer>=0xff0000 else rom;offset=pointer&65535 if pointer>=0xff0000 else pointer
                            raw=data[offset:offset+w*h//2]
                            covered.update(i for i,sx,sy,sw,sh,sraw in sprites if (sx,sy,sw,sh,sraw)==(ax+x,ay+y,w,h,raw))
                visible={i for i,x,y,w,h,raw in sprites if x<320 and x+w>0 and y<224 and y+h>0}
                checks[case+str(age)+'_prepared_inventory_covers_original_sprites']=visible<=covered
    finally:dll.TlkFinalArtFree(art)
    paths=[Path(__file__),source,package,reader_path,ROOT/'tools/audit_pride_final_menu_ram.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,frames=count,image_pixels_compared=compared,
        runtime_reader_inputs='Prepared package only; ROM/WRAM are test oracles',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
