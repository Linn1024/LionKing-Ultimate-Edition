"""Execute original lizard sound gates and bind their ordinary applicability."""
import csv
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
    out=ROOT/'build/pride-lizard-voice73';out.mkdir()
    source=ROOT/'tools/pride_lizard_voice_gate73.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'gate.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'gate.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.lizard_voice_gate73.argtypes=[C.c_uint,C.POINTER(C.c_uint)]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(a,value=None):
        a&=65535
        if value is None:return game.work_ram[a]|game.work_ram[a+1]<<8
        game.work_ram[a]=value&255;game.work_ram[a+1]=(value>>8)&255
    def pointer(a,value):word(a,value>>16);word(a+2,value)
    pointer(0x81c4,0xff98ce)
    def md_gate(counter):
        word(0x98ce+0x2c,counter);cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in ((17,0x2700),(15,0xfffd00),(16,0x19c448)):game.core.m68k_set_reg(reg,value)
        calls=value=0
        for n in range(128):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x19c46a:break
            if pc==0x228a:
                calls+=1;sp=game.core.m68k_get_reg(15);value=word(sp+4)
                ret=word(sp)<<16|word(sp+2);game.core.m68k_set_reg(15,sp+4);game.core.m68k_set_reg(16,ret)
            else:game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD sound gate timeout',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xfffd00
        return [calls,value,word(0x98ce+0x2c)]
    rows=[]
    try:
        for counter in range(65):
            result=(C.c_uint*4)();assert native.lizard_voice_gate73(counter,result)
            other=md_gate(counter);rows.append(dict(counter=counter,snes=list(result),md=other))
    finally:game.close()
    mdreport=ROOT/'build/pride-audio-inventory/report.json';inventory=bound(mdreport)
    native_report=ROOT/'build/pride-hyena-voice70-snes/report.json';bound(native_report)
    native_events=native_report.parent/'events.csv'
    observed_native=[r for r in csv.DictReader(native_events.open()) if r['event']=='0014' and int.from_bytes(bytes.fromhex(r['stack'])[5:8],'little')+1==0xc16527]
    observed_md=[r for r in inventory['original_sound_call_groups'] if r['selector']==2 and r['value']==124 and r['outer_caller']=='19c462' and r['actor_state']=='19c39e']
    checks=dict(all65_native_gates_match=all(r['snes']==([1,20,0,r['counter']] if r['counter']==51 else [0,0,0,r['counter']]) for r in rows),
                all65_md_gates_match=all(r['md']==([1,124,r['counter']] if r['counter']==32 else [0,0,r['counter']]) for r in rows),
                ordinary_native_calls_present=len(observed_native)==8,ordinary_md_calls_present=len(observed_md)==1 and observed_md[0]['count']==10)
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',ROOT/'tools/md_lab.py',snespath,mdpath,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',mdreport,native_report,native_events]
    report=dict(result='CONFIRMED_LIZARD_SOUND_COUNTER_DIFFERENCE' if all(checks.values()) else 'INCOMPLETE',checks=checks,
                native_counter=51,md_counter=32,native_event=20,md_fm=124,
                native_entry_stop=['C1650E','C16529'],md_entry_stop=['19C448','19C46A'],
                intercepted_services=['SNES C22CEC sound','MD00228A FM sound'],ordinary_native_calls=len(observed_native),ordinary_md_calls=observed_md,
                scope='Original sound comparison blocks after their earlier caller guards. No whole action, collision, audio synthesis or display-field-delay proof.',
                runtime_changed=False,public72_publication_still_separate=True,command=command,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
