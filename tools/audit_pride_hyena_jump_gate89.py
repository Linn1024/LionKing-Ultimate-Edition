"""Compare original standing-jump selection and outgoing arguments at matched inputs."""
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
    reference=ROOT/'build/pride-enemy-motion88/report.json';r=bound(reference)
    assert r['result']=='SHARED_ENEMY_MOTION_VERIFIED'
    out=ROOT/'build/pride-hyena-jump-gate89';out.mkdir()
    source=ROOT/'tools/pride_hyena_jump_gate89.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'gate.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'gate.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.hyena_jump_gate89.argtypes=[C.c_int,C.c_int32,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
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
    def md_gate(dx,vy,facing,cycle):
        word(0xfaf8,facing);word(0xfafc,dx);longword(0xfae8,vy&0xffffffff)
        longword(0x81c4,0xff98ce);word(0x98ce+0x28,cycle)
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19af16)]:game.core.m68k_set_reg(reg,value)
        for n in range(512):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc in (0x19af60,0x19afbc,0x19afce):break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD gate timeout',hex(pc)))
        choice=1 if pc==0x19af60 else 2 if pc==0x19afbc else 0
        sp=game.core.m68k_get_reg(15);assert sp==(0xfffcf8 if choice else 0xfffd00)
        return [choice,longword(sp) if choice else 0,longword(sp+4) if choice else 0]
    deltas=list(range(-128,129))+[-2048,-512,512,2048]
    velocities=[-0x80000,-0x30001,-0x30000,-0x2ffff,-1,0,0x80000]
    count=hops=0;failures=[]
    try:
        with (out/'cases.jsonl').open('w') as log:
            for dx,vy,facing,cycle in itertools.product(deltas,velocities,(0,1,2,65535),(0,1,2,65535)):
                raw=(C.c_uint*3)();assert native.hyena_jump_gate89(dx,vy,facing,cycle,raw)
                other=md_gate(dx,vy,facing,cycle);equal=list(raw)==other;count+=1;hops+=bool(raw[0])
                row=dict(dx=dx,player_vy=vy,facing=facing,cycle=cycle,snes=list(raw),md=other,equal=equal)
                log.write(json.dumps(row,separators=(',',':'))+'\n')
                if not equal:failures.append(row)
    finally:game.close()
    checks=dict(all_original_decisions_and_arguments_equal=not failures,all_grid_cases_executed=count==len(deltas)*len(velocities)*16,both_true_and_false_paths_observed=0<hops<count)
    paths=[Path(__file__),reference,source,ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='STANDING_JUMP_GATE_VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,fixtures=count,selected_hops=hops,failures=failures,command=command,
                native_slice=['C13DE3','C13E30','C13E90','C13EA0'],md_slice=['19AF16','19AF60','19AFBC','19AFCE'],
                scope='Cached standing-jump decision after earlier AI/contact/distance guards. Stops before selected action calls, verifying their outgoing arguments. Does not execute the whole AI or action.',
                production_or_capabilities_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],count,'fixtures',hops,'hops',checks,flush=True)


if __name__=='__main__':main()
