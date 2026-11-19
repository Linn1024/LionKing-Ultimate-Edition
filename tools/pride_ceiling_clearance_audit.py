"""Isolate original pose-top clearance at the next rising-jump difference.

The ordinary MD replay supplies the snapshot. Original MD ceiling instructions
are then called with their original top word or the native pose's top word in
a synthetic header. This is an isolated data-source test, not a playthrough.
"""
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from pride_sprite_catalog import read_rom


def main():
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    path=ROOT/'build/pride-ceiling-gap/hl_wram_1040.bin';ram=path.read_bytes()
    nw=lambda p:struct.unpack_from('<H',ram,p)[0];draw=nw(0xb21f)
    native_pose=int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff
    native_top=struct.unpack_from('<h',snes,native_pose+14)[0]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    w=lambda p:game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
    def put(p,v):v&=65535;game.work_ram[p]=v&255;game.work_ram[p+1]=v>>8
    try:
        rows=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
        for row in rows[:1429]:game.step(row['pad']);game.samples.clear()
        x,y=w(0x93d6),w(0x93d8);assert (x,y)==(nw(0xb21b),nw(0xb21d))==(454,1095)
        original=bytes(game.work_ram);draw=w(0x93ce+12);pose=(w(draw+10)<<16|w(draw+12))&0xffffff
        top=struct.unpack_from('>h',md,pose+14)[0];assert native_top==-32 and top==-31
        results=[]
        for clearance in (top,native_top):
            C.memmove(C.addressof(game.work_ram),original,len(original))
            put(0x81c4,0xff);put(0x81c6,0x93ce)
            game.write_code(0xf000,md[pose:pose+20]);put(0xf00e,clearance)
            put(draw+10,0xff);put(draw+12,0xf000)
            game.write_code(0xfe00,bytes.fromhex('4eb9000028fe40c260fe'))
            for reg,value in ((0,x),(1,y),(17,0x2700),(15,0xfffd00),(16,0xfffe00)):game.core.m68k_set_reg(reg,value)
            game.step();result=game.core.m68k_get_reg(0)&0xffffffff
            results.append({'top_word':clearance,'head_y':y+clearance,'map_upper_row':max(0,y+clearance-8)//16,'original_md_result':result})
        assert results[0]['original_md_result']==0 and results[1]['original_md_result']==0xffffffff
        out=ROOT/'build/pride-ceiling-clearance-original';out.mkdir(exist_ok=True)
        report={'result':'PASS','scope':__doc__,'actor_xy':[x,y],'native_pose':native_pose,'md_pose':pose,
            'queries':results,'native_ram_sha256':hashlib.sha256(ram).hexdigest(),
            'md_snapshot_sha256':hashlib.sha256(original).hexdigest()}
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Original MD ceiling: MD top-31 clear, native top-32 blocked at the same position PASS',flush=True)
    finally:game.close()


if __name__=='__main__':main()
