"""Compare original lizard probability decisions and their24-bit RNG updates.

Ordinary snapshots explain a divergent reaction. Isolated calls then compare
both originals with equal seeds, including every output byte and probability
level. Research seed edits are not an authored game route or runtime patch.
Run with the32-bit research Python and current pride_terrain_native.dll.
"""
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from audit_scenes import read_rom


def main():
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(ROOT/'build/pride_terrain_native.dll'))
    native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.terrain_native_probability.argtypes=[C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    assert native.terrain_native_init(snes,len(snes))
    sample_path=ROOT/'build/pride-streaming-contact-history/hl_wram_1574.bin'
    sample=sample_path.read_bytes();nw=lambda a:struct.unpack_from('<H',sample,a)[0]
    native_seed=int.from_bytes(sample[0x1e00:0x1e03],'little')
    assert [nw(0xb413+8),nw(0xb413+10),sample[0xb413+64],nw(0xb413+70)]==[575,687,0x51,36]
    game=MdLab();out=ROOT/'build/pride-reaction-probability';out.mkdir(exist_ok=True)
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    def byte(a):return game.work_ram[a^1]
    def put(a,v):game.work_ram[a]=v&255;game.work_ram[a+1]=(v>>8)&255
    def seed_value():return byte(0x81af)|byte(0x81ae)<<8|byte(0x81ad)<<16
    result=(C.c_uint*4)();live=[];cases=[];blocked=[0]*6
    try:
        rows=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
        for row in rows[:1958]:game.step(row['pad']);game.samples.clear()
        md_sample=bytes(game.work_ram);(out/'md1958-wram.bin').write_bytes(md_sample)
        md_seed=seed_value()
        assert [word(0x9ace+8),word(0x9ace+10),byte(0x9ace+64),word(0x9ace+70)]==[575,687,0x51,36]
        assert native_seed==0x60f4a8 and md_seed==0xa6ba04
        game.write_code(0xfe00,bytes.fromhex('4eb90019956460fe'))
        def query(seed,probability):
            assert native.terrain_native_probability(seed,probability,result)
            for a,shift in ((0x81af,0),(0x81ae,8),(0x81ad,16)):game.work_ram[a^1]=(seed>>shift)&255
            put(0xfd00,probability)
            for reg,value in ((17,0x2700),(15,0xfffd00),(16,0xfffe00)):game.core.m68k_set_reg(reg,value)
            game.step();game.samples.clear()
            value=game.core.m68k_get_reg(0)&65535;updated=seed_value()
            assert value==result[0] and updated==result[1],(seed,probability,list(result),value,updated)
            return {'seed':seed,'probability':probability,'decision':value,'updated_seed':updated,
                    'rng_byte':result[2],'original_native_steps':result[3]}
        for seed in (native_seed,md_seed):live.append(query(seed,1))
        assert [r['decision'] for r in live]==[0,1] and [r['rng_byte'] for r in live]==[188,247]
        for output in range(256):
            encoded=output^128;seed=((encoded&1)*128)<<16|(encoded>>1)<<8
            for probability in range(6):
                row=query(seed,probability)
                if probability not in (0,5):assert row['rng_byte']==output
                expected=probability==5 or (probability>0 and output>255-51*probability)
                assert bool(row['decision'])==expected,(row,output)
                blocked[probability]+=row['decision'];cases.append(row)
        for seed in (0,1,255,256,32768,65535,0x800000,0xffffff,native_seed,md_seed):
            for probability in range(6):cases.append(query(seed,probability))
    finally:game.close()
    payload=json.dumps(cases,separators=(',',':')).encode();(out/'cases.json').write_bytes(payload)
    report={'result':'PASS','scope':__doc__,'original_native_probability':0xc14b70,'original_md_probability':0x199564,
            'original_native_rng':0xc0cbba,'original_md_rng':0xb28,'matrix_cases':len(cases),
            'all_output_bytes_checked':256,'probability_levels_checked':6,'true_counts_per256_outputs':blocked,
            'equal_seed_decisions_and_updated_seeds_match':True,'live_seed_decisions':live,
            'live_enemy_xy':[575,687],'live_terrain_attribute':0x51,'live_pre_tile_column':36,
            'source_sha256':{'native_snapshot':hashlib.sha256(sample).hexdigest(),'md_snapshot':hashlib.sha256(md_sample).hexdigest(),
                             'cases':hashlib.sha256(payload).hexdigest()},
            'original_route_reaction_difference_explained_by_rng_state':True,
            'full_enemy_behavior_or_level_fidelity_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original probability/RNG:1596 cases match; live seeds yield188(no reaction) versus247(reaction) PASS',flush=True)


if __name__=='__main__':main()
