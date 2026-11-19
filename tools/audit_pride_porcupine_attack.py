"""Original CPU attack branches; external services are intercepted, not proved."""
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
    out=ROOT/'build/pride-porcupine-attack';out.mkdir()
    source=ROOT/'tools/pride_porcupine_attack_oracle.c'
    core=ROOT/'engine/snesrecomp/runner/src/snes'
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(core),
             str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,cwd=ROOT,check=True)
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    lib=C.CDLL(str(out/'oracle.dll'));lib.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert lib.terrain_native_init(C.create_string_buffer(snes),len(snes))
    lib.porcupine_native_run.argtypes=[C.c_uint]*7+[C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):
        _fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),
                  ('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value=None):
        if value is None:return (word(at)<<16|word(at+2))&0xffffff
        word(at,value>>16);word(at+2,value)
    def run_md(initialized,timer,wait,persistent,projectile,contact,facing):
        game.core.m68k_pulse_reset();actor=0x944e
        for at in range(actor,actor+128,2):word(at,0)
        pointer(0x81c4,0xff0000|actor);word(actor+8,640);word(actor+10,940)
        word(actor+0x20,facing);word(actor+0x22,persistent);word(actor+0x2c,timer)
        word(actor+0x2e,wait)
        if initialized:pointer(actor+0x30,0x19a446)
        for r in range(16):game.core.m68k_set_reg(r,0)
        game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xffe000)
        game.core.m68k_set_reg(16,0x19a446);pointer(0xe000,0x4000);word(0xe004,persistent)
        calls=[0]*8;next_action=0
        services={0x18eb66:0,0x2ce6:1,0x18f108:2,0x18f192:2,0x199ed4:3,
                  0x18d594:4,0x19a800:5,0x228a:6,0x213e:7}
        for n in range(2048):
            pc=game.core.m68k_get_reg(16)&0xffffff
            assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            if pc in services or pc==0x19a128:
                if pc==0x19a128:next_action+=1
                else:calls[services[pc]]+=1
                game.core.m68k_set_reg(0,contact if pc==0x18d594 else 0)
                sp=game.core.m68k_get_reg(15)
                game.core.m68k_set_reg(16,pointer(sp));game.core.m68k_set_reg(15,sp+4)
            else:game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD action did not finish',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xffe004
        return [word(actor+0x2c),word(actor+0x2e),word(actor+0x28),word(actor+0x2a),
                word(actor+0x3a),word(actor+0x38),word(actor+0x3e),word(actor+0x3c),
                word(actor+0x22),*calls,next_action,n]
    cases=[];checks={}
    def expected(source,initialized,timer,wait,persistent,projectile,contact,facing):
        counts=[0]*8;next_action=0;origin=[0,0];velocity=[0]*4
        if not initialized:
            return [70,30,640,932,0,3,0,65535,persistent,*counts,0]
        counts[0]=1
        if 0<wait<32768:
            wait-=1;counts[1]=1
        else:
            if source=='snes' and timer==20:counts[6]=1
            if 28<timer<32768:
                counts[2]=2;counts[3]=counts[1]=1;timer=(timer-1)&65535
            else:
                counts[4]=int(source=='md' or projectile!=0)
                counts[5]=int(bool(counts[4] and contact))
                if not persistent:timer=0
                if source=='md' and timer==28:counts[6]=1
                if timer:
                    counts[1]=1;timer=(timer-1)&65535
                elif persistent:counts[7]=1
                else:
                    velocity=[0,65535 if facing else 1,0,65534];next_action=1
        return [timer,wait,*origin,*velocity,persistent,*counts,next_action]
    try:
        inputs=itertools.chain(itertools.product((0,),(0,),(0,),(0,1),(0,),(0,),(0,1)),
            itertools.product((1,),(0,1,19,20,21,27,28,29,30,70,65535),(0,1,30,65535),
                              (0,1),(0,1),(0,1),(0,1)))
        for inp in inputs:
            for source_name in ('snes','md'):
                if source_name=='snes':
                    raw=(C.c_uint*20)();assert lib.porcupine_native_run(*inp,raw),inp
                    observed=list(raw)
                else:observed=run_md(*inp)
                exp=expected(source_name,*inp)
                checks[str(len(cases))]=observed[:18]==exp
                cases.append(dict(source=source_name,inputs=list(inp),observed=observed,expected=exp))
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,core/'interp816.h',
           ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
           ROOT/'.tools/genesis-plus-gx/core/m68k/m68k.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                compile_command=command,synthetic_fixtures=True,original_instructions_modified=False,
                field_order=['timer','wait','origin_x','origin_y','vx_low','vx_high','vy_low','vy_high','persistent',
                             'offscreen','animation','facing_services','trajectory','contact','reaction','sound','retire','next_action'],
                native_intercepts=['C194B7','C0AF09','C196FA','C19711','C155A6','C0D512','C13625','C22CEC','C0AC84','C15872'],
                md_intercepts=['18EB66','002CE6','18F108','18F192','199ED4','18D594','19A800','00228A','00213E','19A128'],
                external_callees_proven=False,runtime_adapter_enabled=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                rom_sha256={'snes':digest(ROOT/'Lion King, The (USA).sfc'),'md':digest(ROOT/'Lion King, The (World).md')},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    print('failures',[(r['source'],r['inputs'],r['observed'][:18],r['expected']) for r in cases if r['observed'][:18]!=r['expected']][:4],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
