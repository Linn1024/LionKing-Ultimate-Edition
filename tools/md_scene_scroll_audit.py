"""Compare original MD line-scroll callbacks on isolated arithmetic fixtures.

Copies the original body to research RAM, removing only its final video-stream
call. Does not establish normal gameplay, initialization or completion.
"""
import ctypes as C
import json
import random
import struct
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from md_scene_background import line_offsets
from pride_sprite_catalog import read_rom


def main():
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();out=ROOT/'build/md-scene-scroll-oracle';out.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    def put(a,v):v&=65535;game.work_ram[a]=v&255;game.work_ram[a+1]=v>>8
    def read(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    rng=random.Random(0x8bf34);rows=[]
    try:
        for level,start,end,call in [(1,0x8bb28,0x8bec8,0x8bec0),(2,0x8bf34,0x8c16a,0x8c162)]:
            assert game.core.retro_unserialize(state,len(state)-1)
            camera=read(0xcd36);bg=0xe000
            body=bytearray(rom[start:end]);offset=call-start
            assert body[offset:offset+6]==bytes.fromhex('4eb9000018c0')
            body[offset:offset+6]=bytes.fromhex('4e714e714e71');game.write_code(0xf000,body)
            game.write_code(0xfe00,bytes.fromhex('4eb900fff00060fe'))
            cases=[(x,e) for x in (0,1,31,32,255,256,1023,12000,32767,65535) for e in (0,1,65535)]+[(rng.randrange(65536),rng.randrange(65536)) for _ in range(128)]
            for x,extra in cases:
                put(camera+8,x);put(0xcd00,extra)
                game.core.m68k_set_reg(8,0xff0000|bg);game.core.m68k_set_reg(17,0x2700)
                game.core.m68k_set_reg(15,0xfffd00);game.core.m68k_set_reg(16,0xfffe00);game.step()
                actual=[read(0xc610+2*y) for y in range(224)];expected=[(-v)&1023 for v in line_offsets(level,x+(extra if level==1 else 0))]
                assert actual==expected,(level,x,extra,next((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b))
                rows.append({'level':level,'camera_x':x,'offset':extra,'line_words':actual})
    finally:game.close()
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'cases':len(rows)},indent=2)+'\n')
    with (out/'line-scroll.bin').open('wb') as f:
        f.write(b'MDSCROLL'+struct.pack('<I',len(rows)))
        for row in rows:f.write(struct.pack('<4H224H',row['level'],row['camera_x'],row['offset'],0,*row['line_words']))
    print('Original MD line scroll:',len(rows),'fixtures x 224 lines PASS',flush=True)


if __name__=='__main__':main()
