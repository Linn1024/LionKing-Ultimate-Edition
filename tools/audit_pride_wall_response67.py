"""Compare original wall blocking and horizontal pushout, beyond classification alone.

Synthetic maps/actors belong only to isolated research cores. No production data
or original instructions are replaced. Run with .tools/python32/python.exe.
"""
import ctypes as C
import itertools
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab


def main():
    out=ROOT/'build/pride-wall-response67';out.mkdir()
    source=ROOT/'tools/pride_wall_response_oracle67.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    native.wall_native.argtypes=[C.c_uint]*7+[C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value):word(at,value>>16);word(at+2,value)
    C.memset(C.addressof(game.work_ram),0,65536)
    word(0xcd1e,16);pointer(0xcd22,0xffe000);pointer(0xcd2e,0xffe100)
    pointer(0xcd46,0xff93ce);pointer(0x81c4,0xff93ce);game.work_ram[0xe102^1]=0x10
    previous=[]
    def md_run(left,attribute,below,neighbor,flags,x,y):
        nonlocal previous
        for at in previous:word(at,0)
        row=max(y-8,0)//16;col=x//16
        previous=[0xe000+row*16+col*2,0xe000+(row+1)*16+col*2,0xe000+row*16+(col+(1 if left else -1))*2]
        for at,value in zip(previous,(8,16,24)):word(at,value)
        for at,value in [(0xe106,attribute),(0xe10a,below),(0xe10e,neighbor),(0x93ce+0x43,flags)]:game.work_ram[at^1]=value
        word(0x93ce+8,x+12 if left else x-12);word(0x93ce+10,y+8)
        game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(0,x),(1,y),(8,0xff93ce),(17,0x2700),(15,0xfffd00),(16,0x2570 if left else 0x2468)]:game.core.m68k_set_reg(reg,value)
        pointer(0xfd00,0x4000)
        for n in range(1024):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD helper failed to return',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xfffd04
        return [game.core.m68k_get_reg(17)&1,word(0x93ce+8),word(0x93ce+10),n]
    attributes=[0,2,6,9,0x10,0x11,0x40,0x41,0x4e,0x4f,0xf9,0xfa,0xff]
    ys=[0,7,8,9,15,16,17,23,24,25,31,32,39,40,41,47]
    count=0;failures=[];groups={};samples=[]
    try:
        for left,attr,below,neighbor,flags,x,y in itertools.product((0,1),attributes,(0,6,9,0xff),(0,0x40,0x41,0xff),(0,8),range(32,48),ys):
            result=(C.c_uint*5)();assert native.wall_native(left,attr,below,neighbor,flags,x,y,result)
            other=md_run(left,attr,below,neighbor,flags,x,y);count+=1
            match=list(result[:3])==other[:3]
            key=f'{left}:{attr:02x}';group=groups.setdefault(key,dict(cases=0,mismatches=0,blocking=0,pushouts=0))
            group['cases']+=1;group['mismatches']+=not match;group['blocking']+=result[0]
            group['pushouts']+=result[1]!=(x+12 if left else x-12)
            if not match and len(failures)<64:failures.append(dict(left=left,attribute=attr,below=below,neighbor=neighbor,flags=flags,x=x,y=y,snes=list(result),md=other))
            if len(samples)<32:samples.append(dict(left=left,attribute=attr,below=below,neighbor=neighbor,flags=flags,x=x,y=y,snes=list(result),md=other))
    finally:game.close()
    checks=dict(all212992_fixtures=count==212992,all_blocking_and_actor_xy_match=not any(g['mismatches'] for g in groups.values()),
                both_pushout_directions_exercised=all(any(g['pushouts'] for k,g in groups.items() if k.startswith(str(side)+':')) for side in (0,1)))
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',ROOT/'tools/md_lab.py',snespath,mdpath,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,cases=count,groups=groups,first_mismatches=failures,samples=samples,
                native_entries=['C0C639','C0C723'],md_entries=['002468','002570'],
                scope='Original common-coordinate wall query blocking and actor X/Y; synthetic bounds, not whole actor AI or natural cell reachability',
                production_or_original_code_modified=False,attributes=attributes,y_inputs=ys,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],count,'mismatches',sum(g['mismatches'] for g in groups.values()),failures[:2],flush=True)


if __name__=='__main__':main()
