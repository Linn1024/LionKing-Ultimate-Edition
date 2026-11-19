"""Execute original SNES/MD vertical activation window arithmetic.

Synthetic camera coordinates are confined to research cores. Ordinary-input
birth observations motivate this comparison; this is not a completed route.
Run with the32-bit research Python after building pride_terrain_native.dll.
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
    native=C.CDLL(str(ROOT/'build/pride_terrain_native.dll'))
    native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.terrain_native_spawn_window.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    assert native.terrain_native_init(snes,len(snes))
    sample=(ROOT/'build/pride-porcupine-history/hl_wram_1030.bin').read_bytes()
    rows=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    def put(at,value):game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    result=(C.c_uint*9)();fixtures=[]
    try:
        for row in rows[:1419]:game.step(row['pad']);game.samples.clear()
        camera=word(0xcd36);assert (word(camera+8),word(camera+10))==(259,1039)
        assert [word(at) for at in (0xcd1c,0xcd1e,0xcd20)]==[28,200,80]
        original=bytes(game.work_ram)
        game.write_code(0xfe00,bytes.fromhex('4eb90009270a60fe'))
        for y in range(1280):
            assert native.terrain_native_spawn_window(sample,len(sample),259,y,result)
            put(camera+8,259);put(camera+10,y)
            for reg,value in ((8,0xff0000|camera),(9,0xffe930),(17,0x2700),(15,0xfffd00),(16,0xfffe00)):
                game.core.m68k_set_reg(reg,value)
            game.step();game.samples.clear()
            d=[game.core.m68k_get_reg(i)&65535 for i in range(4)]
            assert result[2]==(y//16)*2
            assert d[2]==max(0,result[2]-12)
            assert d[3]==result[3] and word(0xe930)==result[4] and word(0xe932)==result[5]
            fixtures.append({'camera_y':y,'native_top_index':result[2],'md_top_index':d[2],
                             'shared_bottom_index':d[3],'shared_culling_top':result[4]})
        assert fixtures[1039]['native_top_index']==128 and fixtures[1039]['md_top_index']==116
    finally:game.close()
    out=ROOT/'build/pride-streaming-top-original';out.mkdir(exist_ok=True)
    report={'result':'PASS','scope':__doc__,'original_native_function':0xc0b8ea,'original_md_function':0x9270a,
            'cases':len(fixtures),'all_top_indexes_differ_by_clamped_12':True,'bottom_and_culling_bounds_agree':True,
            'native_sample_sha256':hashlib.sha256(sample).hexdigest(),
            'original_md_sample_sha256':hashlib.sha256(original).hexdigest(),'fixtures':fixtures,
            'full_streaming_or_enemy_behavior_equivalence_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original vertical windows:1280 camera Y fixtures; native unexpanded scan top, MD clamped12-index margin; culling/bottom agree PASS',flush=True)


if __name__=='__main__':main()
