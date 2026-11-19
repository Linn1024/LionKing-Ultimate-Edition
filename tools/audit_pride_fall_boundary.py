"""Execute untouched original bottom-boundary instructions on bounded fixtures.

Use .tools/python32/python.exe. This is arithmetic/branch evidence, not proof
of a naturally reachable Pride fall or a completed fall-death presentation.
"""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))

from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab


def main():
    out=ROOT/'build/pride-fall-boundary';out.mkdir()
    source=ROOT/'tools/pride_fall_boundary_oracle.c'
    core=ROOT/'engine/snesrecomp/runner/src/snes'
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',
         '-I'+str(core),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,cwd=ROOT,check=True)
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    lib=C.CDLL(str(out/'oracle.dll'))
    lib.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert lib.terrain_native_init(C.create_string_buffer(snes),len(snes))
    lib.fall_native_boundary.argtypes=[C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):
        _fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):
        _fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),
                  ('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def md_run(height,y,skip,level):
        game.core.m68k_pulse_reset()
        word(0xccc6,height-224);word(0xccce,level)
        word(0xccf6,6);word(0xe956,skip);word(0x944e+10,y)
        for r in range(16):game.core.m68k_set_reg(r,0)
        game.core.m68k_set_reg(17,0x2700)
        game.core.m68k_set_reg(8,0xff944e)
        game.core.m68k_set_reg(15,0xffe000)
        game.core.m68k_set_reg(16,0x7dd62)
        for n in range(32):
            pc=game.core.m68k_get_reg(16)&0xffffff
            assert cpu.pc&0xffffff==pc
            if pc==0x7dd8e:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD boundary did not finish',hex(pc)))
        return [word(0xccf6),word(0x9458),word(0xe956),n]
    cases=[];checks={}
    try:
        for height in (1024,1280,1536,2048):
            native_limit=height-1+296
            md_limit=height+16
            ys=sorted({0,height-1,height,md_limit-1,md_limit,md_limit+1,
                       native_limit-1,native_limit,native_limit+1,native_limit+100})
            for y in ys:
                for skip in (0,0x1234,0xffff):
                    raw=(C.c_uint*4)();assert lib.fall_native_boundary(height,y,skip,raw)
                    expected=[0 if y>native_limit else 6,native_limit-101 if y>native_limit else y,skip]
                    checks[f'{len(cases)}-snes']=list(raw)[:3]==expected
                    cases.append(dict(source='snes',height=height,y=y,skip=skip,observed=list(raw),expected=expected))
                    for level in (0,4):
                        observed=md_run(height,y,skip,level)
                        dead=level!=4 and y>md_limit
                        expected=[0 if dead else 6,y,0xffff if dead else skip]
                        checks[f'{len(cases)}-md']=observed[:3]==expected
                        cases.append(dict(source='md',height=height,y=y,skip=skip,level=level,observed=observed,expected=expected))
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,
           core/'interp816.h',ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
           ROOT/'.tools/genesis-plus-gx/core/m68k/m68k.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                compile_command=cmd,original_instructions_modified=False,synthetic_fixtures=True,
                native_range=['C0B450','C0B465'],md_range=['07DD62','07DD8E'],
                pride=dict(map_height=1280,snes_first_dead_y=1576,snes_clamped_y=1474,
                           md_first_dead_y=1297,md_clamps_y=False),
                natural_reachability_proven=False,runtime_adapter_enabled=False,
                rom_sha256={'snes':digest(ROOT/'Lion King, The (USA).sfc'),'md':digest(ROOT/'Lion King, The (World).md')},
                original_bytes={'snes':snes[0xb450:0xb465].hex(),'md':md[0x7dd62:0x7dd8e].hex()},
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
