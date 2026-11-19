"""Execute original ceiling helpers on the first rising-jump divergence.

The MD snapshot is obtained through an unforced original-input replay. Isolated
helper calls supply only their call ABI; they do not constitute a playthrough.
Run using .tools/python32/python.exe after building pride_terrain_native.dll.
"""
import ctypes as C
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from pride_sprite_catalog import read_rom


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--matrix',action='store_true');args=parser.parse_args()
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    source=ROOT/'build/pride-md-controller-route/hl_wram_1033.bin';ram=source.read_bytes()
    w=lambda p:struct.unpack_from('<H',ram,p)[0]
    x,y=w(0xb21b),w(0xb21d);assert (x,y)==(426,1112)
    native=C.CDLL(str(ROOT/'build/pride_terrain_native.dll'))
    native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.terrain_native_ceiling_snapshot.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    assert native.terrain_native_init(s,len(s))
    result=(C.c_uint*5)();assert native.terrain_native_ceiling_snapshot(ram,len(ram),x,y,result)
    game=MdLab();out=ROOT/'build/pride-ceiling-original';out.mkdir(exist_ok=True)
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    rows=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
    word=lambda p:game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
    def put(p,value):game.work_ram[p]=value&255;game.work_ram[p+1]=value>>8
    try:
        for row in rows[:1422]:game.step(row['pad']);game.samples.clear()
        assert (word(0x93ce+8),word(0x93ce+10))==(x,y)
        original=bytes(game.work_ram);(out/'md1422-wram.bin').write_bytes(original)
        draw=word(0x93ce+12);pose=(word(draw+10)<<16|word(draw+12))&0xffffff
        top=struct.unpack_from('>h',md,pose+14)[0]
        rowbytes=word(0xcd1e);mapbase=word(0xcd22)<<16|word(0xcd24)
        collision=word(0xcd2e)<<16|word(0xcd30)
        map_address=mapbase+((y+top-8)//16)*rowbytes+(x//16)*2
        names=[word(map_address),word(map_address+rowbytes)]
        attrs=[md[collision+((n&0xfff8)>>1)+2] for n in names]
        put(0x81c4,0xff);put(0x81c6,0x93ce)
        game.write_code(0xfe00,bytes.fromhex('4eb9000028fe40c260fe'))
        for reg,value in ((0,x),(1,y),(17,0x2700),(15,0xfffd00),(16,0xfffe00)):game.core.m68k_set_reg(reg,value)
        game.step();external=game.core.m68k_get_reg(0)&0xffffffff;flags=game.core.m68k_get_reg(2)&0x11
        native_address=result[4];off=native_address-0x7e0000
        native_names=[struct.unpack_from('<H',ram,off)[0],struct.unpack_from('<H',ram,off+w(0xd0))[0]]
        base=w(0xf2)|ram[0xf4]<<16
        def byte_at(a):return ram[a-0x7e0000] if 0x7e0000<=a<0x800000 else s[a-0xc00000]
        native_attrs=[byte_at(base+((n&0xfff8)>>1)) for n in native_names]
        report={'result':'DIFFERENCE','scope':__doc__,'probe_xy':[x,y],'md_pose':pose,'top_offset':top,
            'native_return':list(result),'md_return':external,'md_carry_extend':flags,
            'md_upper_lower_attributes':attrs,'native_upper_lower_attributes':native_attrs,
            'native_ram_sha256':hashlib.sha256(ram).hexdigest(),'md_ram_sha256':hashlib.sha256(original).hexdigest()}
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
        assert result[0]==result[1]==65535 and external==0 and attrs==native_attrs==[255,0]
        if args.matrix:
            # Isolated synthetic map/dictionary, preserving the actual pose
            # headers and all original helper instructions in both cores.
            sample=bytearray(ram)
            def nw(p,value):struct.pack_into('<H',sample,p,value&65535)
            nw(0xe9,0xe000);sample[0xeb]=0x7f;nw(0xd0,2)
            nw(0xf2,0xe102);sample[0xf4]=0x7e
            sample[0x1e000:0x1e080]=bytes(128);sample[0xe100:0xe120]=bytes(32);nw(0x1e004,8)
            for row in range(80):nw(0xa706+row*2,row*2)
            put(0xcd1e,2);put(0xcd22,0xff);put(0xcd24,0xe000);put(0xcd2e,0xff);put(0xcd30,0xe100)
            for p in range(0xe000,0xe080):game.work_ram[p]=0
            for p in range(0xe100,0xe120):game.work_ram[p]=0
            put(0xe004,8)
            fixture=C.create_string_buffer(bytes(sample));outcomes=bytearray();differences=[];blocked=[0,0]
            for upper in range(256):
                fixture[0xe102]=bytes([upper]);game.work_ram[0xe102^1]=upper
                for lower in range(256):
                    fixture[0xe106]=bytes([lower]);game.work_ram[0xe106^1]=lower
                    assert native.terrain_native_ceiling_snapshot(fixture,len(sample),10,64,result)
                    for reg,value in ((0,10),(1,64),(17,0x2700),(15,0xfffd00),(16,0xfffe00)):game.core.m68k_set_reg(reg,value)
                    game.step();game.samples.clear()
                    actual=game.core.m68k_get_reg(0)&0xffffffff;carry=game.core.m68k_get_reg(2)&0x11
                    expected=lower>=0xb0 or 0x40<=lower<0x50
                    assert actual==(0xffffffff if expected else 0) and carry==(0x11 if expected else 0),(upper,lower,actual,carry)
                    a=bool(result[0]);b=bool(actual);blocked[0]+=a;blocked[1]+=b
                    outcomes.extend((a,b))
                    if a!=b and len(differences)<16:differences.append({'upper':upper,'lower':lower,'snes':a,'md':b})
                if upper%32==31:print('Original ceiling matrix:',(upper+1)*256,'cases',flush=True)
            (out/'matrix.bin').write_bytes(outcomes)
            matrix={'result':'PASS','scope':'Untouched original helpers on all256x256 upper/lower attribute pairs, x10/y64, real pose top-33',
                'cases':65536,'md_matches_lower_row_rule_all_cases':True,'snes_blocked':blocked[0],'md_blocked':blocked[1],
                'different_cases':sum(a!=b for a,b in zip(outcomes[::2],outcomes[1::2])),
                'examples':differences,'outcomes_sha256':hashlib.sha256(outcomes).hexdigest(),
                'ordinary_playthrough_proof':False}
            (out/'matrix.json').write_text(json.dumps(matrix,indent=2)+'\n');print(json.dumps(matrix,indent=2),flush=True)
    finally:game.close()


if __name__=='__main__':main()
