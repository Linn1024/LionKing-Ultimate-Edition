"""Compare original AI choice branches for every Pride attribute and RNG byte."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab


def main():
    out=ROOT/'build/pride-porcupine-choice-originals';out.mkdir()
    source=ROOT/'build/pride-nonpersistent-selector/report.json';prior=bound(source);assert prior['result']=='PASS'
    attrs=sorted(set(prior['tables']['snes']['unique_attributes'])|set(prior['tables']['md']['unique_attributes']))
    positive_controls=[0x52,0x53,0xf2,0xf3];attributes=sorted(set(attrs+positive_controls))
    native=ROOT/'tools/pride_porcupine_choice_oracle.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(native),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,check=True)
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    lib=C.CDLL(str(out/'oracle.dll'));lib.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert lib.terrain_native_init(C.create_string_buffer(rom),len(rom))
    lib.pride_porcupine_choice.argtypes=[C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):
        _fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),
                  ('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k');game.work_ram[:]=bytes(65536)
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value=None):
        if value is None:return (word(at)<<16|word(at+2))&0xffffff
        word(at,value>>16);word(at+2,value)
    def run_md(attribute,seed):
        game.core.m68k_pulse_reset();actor=0x944e
        for at in range(actor,actor+128,2):word(at,0)
        pointer(0x81c4,0xff0000|actor);game.work_ram[(actor+0x40)^1]=attribute;pointer(actor+0x30,0x19a128)
        for at,shift in [(0x81af,0),(0x81ae,8),(0x81ad,16)]:game.work_ram[at^1]=(seed>>shift)&255
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(15,0xffe000),(16,0x19a128)]:game.core.m68k_set_reg(reg,value)
        pointer(0xe000,0x4000);counts=[0,0,0];choice=0
        services={0x18eb66:0,0x18d594:0,0x2ce6:0,0x18e962:0,0x18e9f6:0,0x18eae6:0,0x18f108:0,0x18f192:0,0x19a38e:0,0x19961a:1}
        for n in range(4096):
            pc=game.core.m68k_get_reg(16)&0xffffff
            if pc==0x4000:break
            for i,target in enumerate((0x18e8e8,0x199564,0xb28)):
                if pc==target:counts[i]+=1
            if pc in services or pc in (0x199ac8,0x19a446):
                sp=game.core.m68k_get_reg(15)
                if pc==0x199ac8:
                    duration=word(sp+16);assert duration in (10,120),(hex(pc),duration)
                    choice=1 if duration==120 else 2
                elif pc==0x19a446:
                    persistence=word(sp+4);assert persistence in (0,1);choice=3+persistence
                game.core.m68k_set_reg(0,services.get(pc,0));game.core.m68k_set_reg(16,pointer(sp));game.core.m68k_set_reg(15,sp+4)
            else:game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD caller did not return',attribute,hex(pc)))
        assert game.core.m68k_get_reg(15)==0xffe004
        updated=sum(game.work_ram[a^1]<<shift for a,shift in [(0x81af,0),(0x81ae,8),(0x81ad,16)])
        return [choice,updated,*counts]
    cases=[];checks={};decisions={}
    try:
        for attribute in attributes:
            choices=set()
            for output in range(256):
                encoded=output^128;seed=((encoded&1)*128)<<16|(encoded>>1)<<8
                result=(C.c_uint*8)();assert lib.pride_porcupine_choice(attribute,seed,result),(attribute,output)
                md=run_md(attribute,seed);observed=list(result)
                checks[f'choice-{attribute}-{output}']=observed[:5]==md
                choices.add(observed[0]);cases.append(dict(attribute=attribute,seed=seed,native=observed,md=md))
            decisions[str(attribute)]=sorted(choices)
            print(hex(attribute),sorted(choices),flush=True)
    finally:game.close()
    checks['all_authored_attributes_never_choose_nonpersistent']=all(3 not in decisions[str(a)] for a in attrs)
    checks['all_authored_attributes_never_choose_terrain_persistent']=all(4 not in decisions[str(a)] for a in attrs)
    checks['synthetic_nonpersistent_positive_controls']=decisions[str(0xf2)]==[3] and 3 in decisions[str(0x52)]
    checks['synthetic_persistent_positive_controls']=decisions[str(0xf3)]==[4] and 4 in decisions[str(0x53)]
    paths=[Path(__file__),source,native,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',ROOT/'tools/md_lab.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,decisions=decisions,
                compile_command=cmd,authored_attributes=attrs,synthetic_control_attributes=positive_controls,
                original_callers=dict(snes='c15872',md='19a128'),original_selectors_and_rng_executed=True,
                external_contact_animation_motion_and_action_services_intercepted=True,changed_tile_return_supplied=True,
                ordinary_encounter_or_full_dynamic_reachability_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
