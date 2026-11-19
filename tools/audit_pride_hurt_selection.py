"""Execute bounded original hurt selectors; intercept only documented callees.

Synthetic CPU fixtures are separate from natural gameplay observations. Sound,
airborne-predicate internals and selected action bodies are outside this audit.
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
    out=ROOT/'build/pride-ledge-controlled/hurt-selection3';out.mkdir()
    source=ROOT/'tools/pride_hurt_selection_oracle.c'
    core=ROOT/'engine/snesrecomp/runner/src/snes';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    library=out/'native.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(core),'-I'+str(ROOT/'tools'),
        str(source),str(runtime),'-o',str(library)]
    subprocess.run(command,cwd=ROOT,check=True)
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    mdrom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    dll=C.CDLL(str(library));dll.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert dll.terrain_native_init(C.create_string_buffer(rom),len(rom))
    dll.hurt_native_select.argtypes=[C.c_uint,C.c_int,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    # Prefix from the pinned m68k.h. Only read its absolute scheduler clock;
    # validate register views on every step before relying on its ABI layout.
    class MemoryMap(C.Structure):
        _fields_=[(name,C.c_void_p) for name in ('base','read8','read16','write8','write16')]
    class CpuPrefix(C.Structure):
        _fields_=[('map',MemoryMap*256),('poll',C.c_uint*3),('cycles',C.c_int),
            ('refresh_cycles',C.c_int),('cycle_end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=CpuPrefix.in_dll(game.core,'m68k')
    game.core.retro_serialize_size.restype=C.c_size_t;size=game.core.retro_serialize_size();snapshot=C.create_string_buffer(size)
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_serialize(snapshot,size)
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value=None):
        if value is None:return word(at)<<16|word(at+2)
        word(at,value>>16);word(at+2,value)
    def md_select(health,relation,airborne,predicate,flags):
        assert game.core.retro_unserialize(snapshot,size)
        # Initialize a running isolated CPU, independently from the outer frame
        # scheduler's initial halt/reset state. This is not a natural-game run.
        game.core.m68k_pulse_reset()
        a=0x93ce;other=0x944e
        for at in range(a,a+128,2):word(at,0)
        pointer(0x81c4,0xff0000|a);pointer(a+0x24,0xff0000|other)
        word(a+8,1000+relation);word(other+8,1000);word(0xccf6,health);word(0xccf2,24)
        word(a+0x48,65535);word(a+0x4c,0x22 if airborne else 2);game.work_ram[(a+0x43)^1]=flags
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xffe000);game.core.m68k_set_reg(16,0x196a1c)
        audio=predicate_calls=0;selected=0;transitions=0;previous=None
        for instruction in range(512):
            pc=game.core.m68k_get_reg(16)&0xffffff
            assert (cpu.pc&0xffffff)==pc and all(cpu.dar[r]==game.core.m68k_get_reg(r) for r in range(16))
            if pc!=previous:transitions+=1;previous=pc
            if pc in (0x19692e,0x196b4c,0x196d04):selected=pc;break
            if pc in (0x18f0de,0x2210,0x18eae6):
                if pc==0x2210:audio+=1
                if pc==0x18eae6:predicate_calls+=1
                game.core.m68k_set_reg(0,predicate if pc==0x18eae6 else 1)
                sp=game.core.m68k_get_reg(15);game.core.m68k_set_reg(16,pointer(sp));game.core.m68k_set_reg(15,sp+4)
            game.core.m68k_run(cpu.cycles+1)
        assert selected,(health,relation,airborne,predicate,flags,hex(game.core.m68k_get_reg(16)))
        return [selected,0,word(0xccf6),word(0xccf2),word(a+0x46),word(a+0x48),word(a+0x4c),
            game.work_ram[(a+0x43)^1],audio,predicate_calls,transitions]
    rows=[];checks={};pairs={0xc35adf:0x19692e,0xc35d6c:0x196b4c,0xc35f3c:0x196d04}
    try:
        for i,args in enumerate(itertools.product((0,1,2,6,0x7fff,0x8000,0xffff),(-1,0,1),(0,1),(0,1),(4,255))):
            native=(C.c_uint*11)();assert dll.hurt_native_select(*args,native)
            a=list(native);b=md_select(*args);health,relation,airborne,predicate,flags=args
            expected_health=health-1 if 0<health<0x8000 else health
            special=bool(airborne and predicate);fatal=expected_health==0 and not special
            checks[str(i)+'/shared_health_flags_roar_immunity_callees']=a[2:10]==b[2:10]
            checks[str(i)+'/original_health_decrement']=a[2]==b[2]==expected_health
            checks[str(i)+'/expected_selected_branch']=(a[0]==0xc35a82 and b[0]==(0x196b4c if relation>0 else 0x196d04) and a[1]==int(relation>0)) if fatal else pairs.get(a[0])==b[0]
            rows.append(dict(inputs=dict(zip(('health','relative_x','airborne_flag','predicate','actor_flags'),args)),native=a,md=b,fatal_selection_difference=fatal))
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',core/'interp816.c',core/'interp816.h',runtime,
        ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
        ROOT/'.tools/genesis-plus-gx/core/m68k/m68k.h',ROOT/'.tools/genesis-plus-gx/core/m68k/m68kcpu.c']
    report=dict(result='BOUNDED_ORIGINAL_HURT_SELECTION_AUDITED' if all(checks.values()) else 'FAIL',
        checks=checks,fixtures=rows,compile_command=command,
        fatal_selection_differences=sum(r['fatal_selection_difference'] for r in rows),
        synthetic_isolated_cpu_fixtures=True,rom_instructions_modified=False,
        intercepted_native_callees=['C22CEC sound','C1946B airborne predicate'],
        intercepted_md_callees=['18F0DE fixed 1..1 selector','002210 sound','18EAE6 airborne predicate'],
        selected_action_bodies_executed=False,natural_contact_timing_equivalence_proven=False,
        death_gameplay_adapter_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(rows),'fixtures',report['fatal_selection_differences'],'fatal differences; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
