"""Execute both original idle roar helpers without intercepting their callees."""
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
    out=ROOT/'build/pride-porcupine-idle';out.mkdir()
    source=ROOT/'tools/pride_porcupine_idle_oracle.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    core=ROOT/'engine/snesrecomp/runner/src/snes'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(core),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,cwd=ROOT,check=True)
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    native.porcupine_idle_native.argtypes=[C.c_int,C.c_int,C.c_uint,C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):
        _fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value=None):
        if value is None:return (word(at)<<16|word(at+2))&0xffffff
        word(at,value>>16);word(at+2,value)
    def run_md(dx,dy,strength):
        game.core.m68k_pulse_reset();actor=0x98ce;player=0x93ce
        for at in range(actor,actor+128,2):word(at,0)
        for at in range(player,player+128,2):word(at,0)
        pointer(0x81c4,0xff0000|actor);pointer(0xcd46,0xff0000|player);word(0xccf4,strength)
        word(actor+8,800);word(actor+10,640);word(player+8,800+dx);word(player+10,640+dy)
        pointer(actor+0x30,0x19a128);pointer(actor+0xe,0xb8a7c)
        word(actor+0x2c,0x55);word(actor+0x2e,0x66);word(actor+0x22,0)
        for r in range(16):game.core.m68k_set_reg(r,0)
        game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xffe000);game.core.m68k_set_reg(16,0x19a086)
        pointer(0xe000,0x4000)
        for n in range(2048):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD helper did not finish',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xffe004
        reacted=pointer(actor+0x30)==0x19a446
        return [int(reacted),word(actor+0x2c),word(actor+0x2e),word(actor+0x22),int(pointer(actor+0xe)==(0xb8acc if reacted else 0xb8a7c)),n]
    magnitudes=(0,1,49,50,51,57,58,65,66,89,90,97,98,127,256,512)
    coordinates=sorted({sign*x for x in magnitudes for sign in (-1,1)})
    checks={};cases=[]
    try:
        for dx,dy,strength in itertools.product(coordinates,coordinates,range(33)):
            raw=(C.c_uint*7)();assert native.porcupine_idle_native(dx,dy,strength,raw),(dx,dy,strength)
            external=run_md(dx,dy,strength)
            distance=max(abs(dx),abs(dy));effective=strength-max(0,distance-50)//8
            reacted=effective>10
            expected=[int(reacted),28 if reacted else 0x55,0 if reacted else 0x66,int(reacted),1]
            checks[str(len(cases))]=list(raw)[:5]==external[:5]==expected and raw[5]==0x77
            cases.append(dict(dx=dx,dy=dy,strength=strength,native=list(raw),md=external,expected=expected))
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,core/'interp816.h',ROOT/'tools/md_lab.py',
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'.tools/genesis-plus-gx/core/m68k/m68k.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,compile_command=command,
        original_helpers=['C157E2','19A086'],intercepted_callees=[],synthetic_fixtures=True,
        natural_idle_response_proven=False,production_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        rom_sha256={'snes':digest(ROOT/'Lion King, The (USA).sfc'),'md':digest(ROOT/'Lion King, The (World).md')},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'paired original executions',flush=True)
    print('failures',[c for c in cases if c['native'][:5]!=c['expected'] or c['md'][:5]!=c['expected']][:2],flush=True)


if __name__=='__main__':main()
