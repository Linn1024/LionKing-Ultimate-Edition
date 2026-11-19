"""Run isolated original MD leaf emitters and capped gravity arithmetic.

Controlled actor fixtures verify the original six-particle cap and one parent
sound; these fixtures are not a normal gameplay or completion reference.
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


def main():
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert rom[0x19c886:0x19c88c]==bytes.fromhex('243c00001000')
    game=MdLab();out=ROOT/'build/pride-leaf-original';out.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    def word(a,v):v&=65535;game.work_ram[a]=v&255;game.work_ram[a+1]=v>>8
    def longword(a,v):word(a,v>>16);word(a+2,v)
    def read(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    def invoke(code):
        game.write_code(0xfe00,code)
        game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xfffd00)
        game.core.m68k_set_reg(16,0xfffe00);game.step()
    counts=[];arithmetic=[]
    try:
        for count in range(7):
            assert game.core.retro_unserialize(state,len(state)-1)
            actor=0xe000;player=read(read(0xcd36)+0x24)
            for a in range(actor,actor+128):game.work_ram[a]=0
            longword(0x81c4,0xff0000|actor)
            longword(0xcd46,0xff0000|player)
            word(actor+8,read(player+8));word(actor+10,read(player+10))
            game.work_ram[(actor+0x43)^1]=1 # Original offscreen test bypass for this isolated actor.
            word(0xe9bc,count)
            path=out/f'cap-{count}.csv'
            assert trace.md_commands_init(game.core._handle,str(path).encode())
            invoke(bytes.fromhex('4eb90019c60460fe'));trace.md_commands_close()
            actual=read(0xe9bc);assert actual==min(6,count+3),(count,actual)
            import csv
            cues=[r for r in csv.DictReader(path.open()) if int(r['selector'])==2 and int(r['value'])==94]
            assert len(cues)==1,(count,cues)
            counts.append({'initial':count,'after':actual,'rustles':len(cues)})
        # Execute the unmodified helper used at 19C898 with the leaf's 0x1000
        # acceleration, retaining signed addition and the seven-pixel cap.
        assert game.core.retro_unserialize(state,len(state)-1)
        rng=random.Random(0x19c886)
        velocities=[-0x40000,-1,0,1,0x6efff,0x6f000,0x6ffff,0x70000]+[rng.randrange(-0x40000,0x70001) for _ in range(256)]
        for velocity in velocities:
            code=bytes.fromhex('2f3c000010002f3c')+struct.pack('>I',velocity&0xffffffff)+bytes.fromhex('4eb90018ecf6508f60fe')
            invoke(code);value=game.core.m68k_get_reg(0)
            expected=min(0x70000,velocity+0x1000)&0xffffffff
            assert value==expected,(velocity,value,expected)
            arithmetic.append({'velocity':velocity,'after':value})
    finally:
        trace.md_commands_close();game.close()
    report={'result':'PASS','scope':__doc__,'emitters':counts,'gravity_cases':len(arithmetic),'gravity':arithmetic}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD leaves: seven spawn-cap cases and',len(arithmetic),'gravity cases PASS',flush=True)


if __name__=='__main__':main()
