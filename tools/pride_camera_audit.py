"""Check Pride Lands camera arithmetic against the original MD instruction body.

The original body is copied into research RAM; only its final streaming call is
replaced with NOPs. This verifies arithmetic, not the video/spawn integration.
"""
import ctypes as C
import json
import random
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from pride_sprite_catalog import read_rom

def signed(n):return (n+32768)%65536-32768

def advance(position,fraction,error,minimum,maximum):
    velocity=(signed(error)<<16)>>3
    if velocity and -65536<velocity<65536:velocity=65536 if velocity>0 else -65536
    if velocity>8*65536:position+=8
    elif velocity<-8*65536:position-=8
    else:
        total=(position<<16)+fraction+velocity
        position=total>>16;fraction=total&65535
    return max(minimum,min(maximum,position)),fraction

def model(case):
    cx,cy,fx,fy,look,px,py,left,flags,frozen=case
    if frozen:return [cx,cy,fx,fy,look,128]
    look=min(192,look+1) if left else max(128,look-1)
    cx,fx=advance(cx,fx,px-cx-look,0,1280)
    target=64 if flags&2 else 210 if flags&1 else 128
    error=signed(py-cy-target)
    if not flags&3:error=min(0,error+20) if error<0 else max(0,error-20)
    cy,fy=advance(cy,fy,error,16,1056)
    return [cx,cy,fx,fy,look,target]

def main():
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();dest=ROOT/'build/pride-camera';dest.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(state)-1)
    def word(at,value):value&=65535;game.work_ram[at]=value&255;game.work_ram[at+1]=value>>8
    def read(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    camera=read(0xcd36);actor=read(camera+0x24);draw=read(actor+12)
    assert [read(camera+off) for off in (0x2e,0x30,0x32,0x34)]==[128,210,64,20]
    body=bytearray(rom[0x8b7f2:0x8ba28]);end=0x8ba1c-0x8b7f2
    assert body[end:end+6]==bytes.fromhex('4eb90000188a')
    body[end:end+6]=bytes.fromhex('4e714e714e71');game.write_code(0xf000,body)
    game.write_code(0xfe00,bytes.fromhex('4eb900fff00060fe'))
    word(0xccfe,0);word(0xe9d4,0);word(0xccc8,1280);word(0xccc6,1056)
    rng=random.Random(1590);cases=[]
    for i in range(1500):
        cases.append([rng.choice([0,1,127,800,1279,1280]),rng.choice([16,17,500,1055,1056]),
                      rng.choice([0,1,8192,32768,65535]),rng.choice([0,1,8192,32768,65535]),
                      rng.choice([80,127,128,160,176,192,193]),rng.randrange(1600),rng.randrange(1280),
                      rng.randrange(2),rng.randrange(4),int(i%31==0)])
    results=[]
    for case in cases:
        cx,cy,fx,fy,look,px,py,left,flags,frozen=case
        for offset,value in [(8,cx),(10,cy),(12,cx),(14,cy),(0x26,fx),(0x28,fy),(0x2a,look),(0x2c,128)]:word(camera+offset,value)
        word(actor+8,px);word(actor+10,py);word(draw+8,0x800 if left else 0)
        game.work_ram[(actor+0x43)^1]=flags;word(0xe9b4,frozen)
        game.core.m68k_set_reg(8,0xff0000|camera);game.core.m68k_set_reg(17,0x2700)
        game.core.m68k_set_reg(15,0xfffd00);game.core.m68k_set_reg(16,0xfffe00);game.step()
        actual=[read(camera+off) for off in (8,10,0x26,0x28,0x2a,0x2c)];expected=model(case)
        assert actual==expected,(case,actual,expected)
        results.append({'input':case,'output':actual})
    game.close()
    report={'result':'PASS','scope':__doc__,'cases':len(results),'results':results}
    (dest/'original-camera-math.json').write_text(json.dumps(report,indent=2)+'\n')
    with (dest/'original-camera-math.bin').open('wb') as reference:
        reference.write(b'CAM1'+struct.pack('<I',len(results)))
        for result in results:reference.write(struct.pack('<16H',*result['input'],*result['output']))
    print('Original MD Pride Lands camera arithmetic:',len(results),'cases match')

if __name__=='__main__':main()
