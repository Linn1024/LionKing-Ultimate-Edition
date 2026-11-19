"""Verify MD meter recipes against their original 68000 generators.

Run with .tools/python32/python.exe. Outputs are local, not game assets to commit.
"""
import ctypes as C
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from pride_sprite_catalog import read_rom

def generate(rom,kind,maximum,current):
    # Kind 0: left roar meter, units 16..48. Kind 1: right health, 4..14.
    maximum=max(4 if kind else 16,min(14 if kind else 48,maximum))
    current=max(0,min(maximum,current));count=max(2,min(9,maximum>>(1 if kind else 3)))
    remaining=current if kind else current>>2
    cap=0x8fa86 if kind else 0x8ec14
    bodies=[0x8fb06,0x8fbc6,0x8fc86] if kind else [0x8ec94,0x8ed54,0x8ee14]
    output=bytearray(rom[cap:cap+64])
    for i in range(count):
        source=bodies[i%3]
        if remaining>0:
            remaining-=2;source+=(2+min(0,remaining))*64
        else:
            remaining-=1
            if remaining!=-1:source=0x8fac6
        output.extend(rom[source:source+64])
    end=0x8fd46 if current==maximum else 0x8fd86
    output.extend(rom[end:end+64]);output.extend(bytes((9-count)*64))
    assert len(output)==704
    return bytes(output)

def main():
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();dest=ROOT/'build/pride-hud';dest.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(state)-1)
    def word(at,value):game.work_ram[at]=value&255;game.work_ram[at+1]=value>>8
    def long(at,value):word(at,value>>16);word(at+2,value&65535)
    cases=0
    with (dest/'original-meter-reference.bin').open('wb') as reference:
        for kind in (0,1):
            for maximum in range(4 if kind else 16,(14 if kind else 48)+1,2 if kind else 8):
                for current in range(maximum+1):
                    base=0x97ce if kind else 0x96ce
                    word(0xccf8 if kind else 0xccf0,maximum);word(0xccf6 if kind else 0xccf2,current)
                    word(base+8+14,0xffff);word(base+8+16,0xffff);long(0x81c4,0xff0000|base)
                    fn=0x8fe7e if kind else 0x8effc
                    game.write_code(0xfe00,bytes.fromhex('4eb9')+struct.pack('>I',fn)+bytes.fromhex('60fe'))
                    game.core.m68k_set_reg(8,0xff0000|base+8)
                    game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xfffd00);game.core.m68k_set_reg(16,0xfffe00)
                    game.step();at=0xecd6 if kind else 0xe9d6;raw=bytes(game.work_ram[at:at+704])
                    actual=bytearray(704);actual[::2]=raw[1::2];actual[1::2]=raw[::2]
                    expected=generate(rom,kind,maximum,current)
                    assert actual==expected,(kind,maximum,current,[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:5])
                    reference.write(struct.pack('<3H',kind,maximum,current)+actual);cases+=1
    game.close();print('Original MD roar/health meter generation:',cases,'cases byte-identical')

if __name__=='__main__':main()
