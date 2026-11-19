"""Compare original pounce gates, executing their terrain/orientation helpers."""
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
from pride_arena_history import bound


def main():
    reference=ROOT/'build/pride-hyena-close-gate91/report.json'
    assert bound(reference)['result']=='CLOSE_ACTION_GATES_VERIFIED'
    out=ROOT/'build/pride-hyena-pounce-gate93';out.mkdir()
    source=ROOT/'tools/pride_hyena_pounce_gate93.c'
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',
             '-I'+str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(runtime),'-o',str(out/'gate.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'gate.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.hyena_pounce_gate93.argtypes=[C.c_int,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def longword(at,value=None):
        if value is None:return word(at)<<16|word(at+2)
        word(at,value>>16);word(at+2,value)
    def md_gate(dx,terrain,tag,facing,ground):
        word(0xfaec,ground);word(0xfaf6,tag);word(0xfaf8,facing);word(0xfafc,dx)
        longword(0x81c4,0xff98ce);word(0x98ce+0x20,facing)
        word(0x98ce+0x40,terrain<<8)  # byte at even guest address is high word byte
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19afce)]:game.core.m68k_set_reg(reg,value)
        for n in range(2048):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc in (0x19b046,0x19b0d0,0x19b0e2):break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD pounce timeout',hex(pc)))
        choice=1 if pc==0x19b046 else 2 if pc==0x19b0d0 else 0
        sp=game.core.m68k_get_reg(15);assert sp==(0xfffcf8 if choice else 0xfffd00)
        assert game.core.m68k_get_reg(14)==0xfffb00
        return [choice,longword(sp) if choice else 0,longword(sp+4) if choice else 0]
    boundaries=[-512,-201,-200,-199,-41,-40,-39,0,39,40,41,199,200,201,512]
    # Complete byte domain at selection thresholds, plus every nearby integer
    # distance for each orientation and all terrain classes that can veto it.
    grid=itertools.product(boundaries,range(256),(0,2,65535),(0,1,2,65535),(0,1))
    sweep=itertools.product(range(-256,257),(0,0x10,0x11,0x53,0x63,0x73,0xb3,0xc3,0xf9,0xfa,0xed,0xee,0xeb,0xec,0x8c,0x8d,0x8e,0x8f),(2,),(0,1),(1,))
    count=0;outcomes=[0,0,0];failures=[]
    try:
        with (out/'cases.jsonl').open('w') as log:
            for dx,terrain,tag,facing,ground in itertools.chain(grid,sweep):
                raw=(C.c_uint*3)();assert native.hyena_pounce_gate93(dx,terrain,tag,facing,ground,raw),(dx,terrain,tag,facing,ground)
                other=md_gate(dx,terrain,tag,facing,ground);equal=list(raw)==other
                count+=1;outcomes[raw[0]]+=1
                row=dict(dx=dx,terrain=terrain,tag=tag,facing=facing,ground=ground,snes=list(raw),md=other,equal=equal)
                log.write(json.dumps(row,separators=(',',':'))+'\n')
                if not equal:failures.append(row)
    finally:game.close()
    expected=len(boundaries)*256*3*4*2+513*18*2
    checks=dict(all_original_decisions_and_arguments_equal=not failures,all_cases_executed=count==expected,all_three_outcomes_observed=all(outcomes))
    paths=[Path(__file__),reference,source,ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='POUNCE_GATES_VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,fixtures=count,outcomes=outcomes,failures=failures,command=command,
                native_slice=['C13EA0','C13F10','C13F93','C13FA3'],md_slice=['19AFCE','19B046','19B0D0','19B0E2'],
                complete_helpers_snes=['C19399','C19415','C193E1','C1371F'],complete_helpers_md=['18E8E8','18E9F6','18E962','19A8AA'],
                scope='Cached pounce decisions after earlier guards. Complete original terrain/orientation helper execution, no interception. Terrain byte0..255 with neighboring byte zero. Stops before selected action; no whole AI, action or collision proof.',
                production_or_capabilities_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],count,'fixtures',outcomes,checks,flush=True)


if __name__=='__main__':main()
