"""Compare the original MD RNG instruction routine with the native SNES algorithm.

This is an isolated arithmetic oracle. It does not establish identical random
call order, seed initialization timing, enemy behavior or complete gameplay.
Run with the 32-bit research Python.
"""
import ctypes as C
import json
import random
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from pride_sprite_catalog import read_rom


def snes_step(seed):
    low=seed&255;middle=(seed>>8)&255;high=(seed>>16)&255
    # C0CBBA: LSR twice, ROL high/middle, SBC low, LSR, ROR low.
    high_new=((high<<1)|((low>>1)&1))&255
    middle_new=((middle<<1)|(high>>7))&255
    difference=((low>>2)-low-(1-(middle>>7)))&255
    low_new=(low>>1)|((difference&1)<<7)
    return high_new<<16|middle_new<<8|low_new,low_new^middle_new


def main():
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert md[0xb16:0xb1c]==bytes.fromhex('349f285a81ac'),'Original MD initialization changed'
    game=MdLab();dest=ROOT/'build/pride-rng';dest.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(state)-1)
    game.write_code(0xfe00,bytes.fromhex('4eb900000b2860fe'))
    randomizer=random.Random(0x9f285a)
    seeds=[0,1,0xffffff,0x9f285a,0xa35700,0xa35757]+[randomizer.randrange(1<<24) for _ in range(4096)]
    results=[]
    try:
        for seed in seeds:
            for address,shift in ((0x81ad,16),(0x81ae,8),(0x81af,0)):
                game.work_ram[address^1]=(seed>>shift)&255
            game.core.m68k_set_reg(0,0xdeadbeef)
            game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xfffd00)
            game.core.m68k_set_reg(16,0xfffe00);game.step()
            actual_seed=sum(game.work_ram[address^1]<<shift for address,shift in ((0x81ad,16),(0x81ae,8),(0x81af,0)))
            actual_value=game.core.m68k_get_reg(0)
            assert (actual_seed,actual_value)==snes_step(seed),(hex(seed),hex(actual_seed),actual_value,snes_step(seed))
            results.append({'seed':seed,'next_seed':actual_seed,'value':actual_value})
    finally:game.close()
    report={'result':'PASS','scope':__doc__,'cases':len(results),'md_initial_seed':0x9f285a,'results':results}
    (dest/'original-rng.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD RNG / native SNES arithmetic:',len(results),'cases identical',flush=True)


if __name__=='__main__':main()
