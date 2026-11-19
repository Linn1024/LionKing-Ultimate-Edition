"""Execute the original hyena contact-response helpers across flags/velocity.

These fixtures begin after geometric overlap. They test pending-hit selection,
not complete boss AI, body rectangles, attack timing or applied damage.
Run with .tools/python32/python.exe.
"""
import ctypes as C
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab


def main():
    out=ROOT/'build/pride-hyena-contact58';out.mkdir()
    source=ROOT/'tools/pride_hyena_contact_oracle.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    native.hyena_native_contact.argtypes=[C.c_uint,C.c_int32,C.c_uint,C.POINTER(C.c_uint)]
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
    def md_run(conditional,velocity,flags):
        game.core.m68k_pulse_reset();actor=0x98ce;player=0x93ce
        for at in range(actor,actor+128,2):word(at,0)
        for at in range(player,player+128,2):word(at,0)
        pointer(0x81c4,0xff0000|actor);pointer(0xcd46,0xff0000|player)
        pointer(player+0x3c,velocity&0xffffffff);game.work_ram[(player+0x43)^1]=flags
        word(0xccf6,6);word(actor+0x2a,2)
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(0,0x1234),(17,0x2700),(15,0xffe000),(16,0x19a824 if conditional else 0x19a800)]:game.core.m68k_set_reg(reg,value)
        pointer(0xe000,0x4000)
        for n in range(1024):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD helper did not return',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xffe004
        return [game.core.m68k_get_reg(0)&65535,game.work_ram[(player+0x43)^1],int(pointer(player+0x24)==0xff0000|actor),word(0xccf6),word(actor+0x2a),n]
    reference=ROOT/'build/pride-hyena-recovery/snes/report.json';assert bound(reference)['result']=='CAPTURED'
    natural=set();captures=[]
    for name in ('normal','hard'):
        for path in sorted((reference.parent/name).glob('hl_wram_*.bin')):
            ram=path.read_bytes();natural.add((ram[0xb213+0x43],struct.unpack_from('<i',ram,0xb213+0x3c)[0]));captures.append(path)
    velocities=(-0x100000,-0x40000,-0x30000,-0x10000,-1,0,1,0x3fff,0x4000,0x4001,0x7fff,0x8000,0x10000,0x30000,0x40000,0x80000,0x100000)
    fixtures=[(1,flags,velocity,'threshold-grid') for flags,velocity in itertools.product(range(256),velocities)]
    fixtures += [(1,flags,velocity,'natural-state-input') for flags,velocity in sorted(natural)]
    fixtures += [(0,flags,0,'ordinary-contact') for flags in range(256)]
    rows=[];failures=[];stress=[]
    try:
        for conditional,flags,velocity,origin in fixtures:
            raw=(C.c_uint*6)();assert native.hyena_native_contact(conditional,velocity,flags,raw)
            other=md_run(conditional,velocity,flags)
            reacted=conditional and velocity>0x4000 and bool(flags&0x18)
            expected=[(0xffff if reacted else 0) if conditional else 0x1234,flags|(0x20 if reacted else 4),1,6,2]
            item=dict(conditional=conditional,flags=flags,velocity=velocity,origin=origin,snes=list(raw),md=other,expected=expected)
            rows.append(item)
            if list(raw)[:5]!=expected or other[:5]!=expected:failures.append(item)
        for velocity,flags in itertools.product((-0x80000000,-0x80000000+0x4000,-0x80000000+0x4001,0x7fffffff),(0,8,16,24)):
            raw=(C.c_uint*6)();assert native.hyena_native_contact(1,velocity,flags,raw)
            other=md_run(1,velocity,flags)
            stress.append(dict(velocity=velocity,flags=flags,snes=list(raw),md=other,equal=list(raw)[:5]==other[:5]))
    finally:game.close()
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'stress.json').write_text(json.dumps(stress,indent=2)+'\n')
    checks=dict(all_threshold_and_natural_inputs_match=not failures,all256_ordinary_contact_flags_executed=sum(r['origin']=='ordinary-contact' for r in rows)==256,
                all4352_threshold_grid_cases_executed=sum(r['origin']=='threshold-grid' for r in rows)==4352,
                natural_fight_inputs_present=bool(natural),
                original_native_pant_helper_call=snes[0x145d3:0x1470f].count(bytes.fromhex('225d36c1'))==1,
                original_md_pant_helper_call=md[0x19b87e:0x19b884]==bytes.fromhex('4eb90019a824'),
                health_unchanged_in_every_fixture=all(r['snes'][3:5]==r['md'][3:5]==[6,2] for r in rows),
                extreme_comparison_results_retained=len(stress)==16)
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',
           ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',snespath,mdpath,reference,*captures]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,case_count=len(rows),natural_unique_inputs=len(natural),
                normal_domain_failures=failures,extreme_differences=[r for r in stress if not r['equal']],
                compile_command=cmd,original_instructions_modified=False,synthetic_original_execution=True,
                geometric_overlap_precondition_assumed=True,whole_ai_or_applied_damage_equivalence=False,
                runtime_adapter_enabled=False,public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],len(rows),'cases',len(natural),'natural inputs',len(failures),'failures',len(report['extreme_differences']),'extreme differences',flush=True)


if __name__=='__main__':main()
