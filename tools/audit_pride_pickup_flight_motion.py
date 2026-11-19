"""Original-CPU flight arithmetic and natural motion-stream evidence.

Run with .tools/python32/python.exe. Synthetic actions intercept only flags,
animation displacement, spawn and retirement; natural trace remains separate.
"""
import csv
import argparse
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


class Motion(C.Structure):
    _fields_=[('x',C.c_uint16),('y',C.c_uint16),('step',C.c_uint16)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='build/pride-pickup-flight-motion2');args=ap.parse_args()
    out=ROOT/args.output;out.mkdir();checks={};cases=[]
    source=ROOT/'tools/pride_pickup_flight_oracle.c'
    core=ROOT/'engine/snesrecomp/runner/src/snes';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    model=ROOT/'engine/runner/tlk_pickup_flight_motion.c'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-Wl,--export-all-symbols','-I'+str(core),str(source),str(runtime),str(model),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,check=True,cwd=ROOT)
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    mdrom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    lib=C.CDLL(str(out/'oracle.dll'));lib.flight_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert lib.flight_native_init(C.create_string_buffer(snes),len(snes))
    lib.flight_native_run.argtypes=[C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_int,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    lib.TlkPickupFlightBegin.argtypes=[C.POINTER(Motion),C.c_uint16,C.c_uint16,C.c_uint16,C.c_uint16];lib.TlkPickupFlightBegin.restype=C.c_bool
    lib.TlkPickupFlightAdvance.argtypes=[C.POINTER(Motion),C.c_uint16,C.c_uint16,C.c_int,C.c_bool];lib.TlkPickupFlightAdvance.restype=C.c_bool
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
        if value is None:return word(at)<<16|word(at+2)
        word(at,value>>16);word(at+2,value)
    def md_run(right,initialized,x,y,step,dx,camera_x,camera_y):
        game.core.m68k_pulse_reset();actor=0x944e;camera=0x93ce
        for at in range(actor,actor+128,2):word(at,0)
        pointer(0x81c4,0xff0000|actor);word(0xcd36,camera)
        word(camera+8,camera_x);word(camera+10,camera_y)
        word(actor+8,x);word(actor+10,y);word(actor+0x34,step)
        entry=0x18f6a2 if right else 0x18f87e
        if initialized:pointer(actor+0x30,entry)
        for at in range(0xccf2,0xcd00,2):word(at,0)
        for register in range(16):game.core.m68k_set_reg(register,0)
        game.core.m68k_set_reg(17,0x2700);game.core.m68k_set_reg(15,0xffe000);game.core.m68k_set_reg(16,entry)
        pointer(0xe000,0x4000);counts=[0,0,0,0]
        assert all(cpu.dar[r]==game.core.m68k_get_reg(r) for r in range(16))
        for instruction in range(2048):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            if pc in (0x18f050,0x2ce6,0x218e,0x213e):
                i=(0x18f050,0x2ce6,0x218e,0x213e).index(pc);counts[i]+=1
                if i==1:word(actor+8,word(actor+8)+dx)
                sp=game.core.m68k_get_reg(15);game.core.m68k_set_reg(16,pointer(sp));game.core.m68k_set_reg(15,sp+4)
            else:game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD action did not return',right,initialized,x,y,hex(pc)))
        assert game.core.m68k_get_reg(15)==0xffe004
        return [word(actor+8),word(actor+10),word(actor+0x34),*counts,instruction]
    try:
        for initialized in (False,True):
            products=itertools.product((False,True),(-16,16,28,128,218,300,340),(0,20,22,24,26,64,108,223),(-3,0,3),(-2,0,2)) if initialized else itertools.product((False,True),(-16,16,28,128,218,300,340),(0,20,22,24,26,64,108,223),(0,),(0,))
            for right,x,y,step,dx in products:
                inp=(right,initialized,x&65535,y,step&65535,dx,32,40)
                for version in ('snes','md'):
                    if version=='snes':
                        raw=(C.c_uint*10)();assert lib.flight_native_run(*inp,raw),('native',inp)
                        observed=list(raw);target_x=232 if right else 16;target_y=24
                    else:observed=md_run(*inp);target_x=300 if right else 16;target_y=20
                    motion=Motion(inp[2],y,inp[4]);arrived=False
                    if initialized:arrived=lib.TlkPickupFlightAdvance(C.byref(motion),target_x,target_y,dx,right)
                    else:
                        sx=(x-32)&65535;sy=(y-40)&65535
                        assert lib.TlkPickupFlightBegin(C.byref(motion),sx,sy,target_x,target_y)
                    expected=[motion.x,motion.y,motion.step,0 if initialized else 1,1 if initialized else 0,int(arrived),int(arrived)]
                    key=f'{len(cases)}-{version}'
                    checks[key]=observed[:7]==expected
                    cases.append(dict(version=version,inputs=list(inp),observed=observed,expected=expected))
        tokens=[];s=0x23a72;m=0x93818
        while snes[s]<128:
            a=list(snes[s:s+3]);b=list(mdrom[m:m+4]);assert a==b[:3] and b[3]==0
            tokens.append(a);s+=3;m+=4
        checks['motion_tokens_match']=len(tokens)==10 and snes[s]==mdrom[m]==255 and int.from_bytes(snes[s+1:s+4],'little')==0xc23a72 and int.from_bytes(mdrom[m+1:m+4],'big')==0x93818
        wave=[dx if dx<128 else dx-256 for duration,dx,dy in tokens for _ in range(duration+1)]
        trace=ROOT/'build/md-pickup-flight/calls.csv';rows=list(csv.DictReader(trace.open()))
        natural=[]
        for action in ('18f6a2','18f87e'):
            flight=[r for r in rows if r['callback']==r['action']==action and int(r['flags'],16)&0x40]
            motion=Motion();right=action=='18f6a2';target=300 if right else 16
            assert lib.TlkPickupFlightBegin(C.byref(motion),int(flight[0]['x']),int(flight[0]['y']),target,20)
            for i,(before,after) in enumerate(zip(flight,flight[1:])):
                assert int(after['field'])==int(before['field'])+1
                retired=lib.TlkPickupFlightAdvance(C.byref(motion),target,20,wave[i%len(wave)],right)
                checks[f'natural-{action}-{i}']=(motion.x,motion.y)==(int(after['x']),int(after['y'])) and not retired
            checks[f'natural-{action}-last-retires']=lib.TlkPickupFlightAdvance(C.byref(motion),target,20,wave[(len(flight)-1)%len(wave)],right)
            natural.append(dict(action=action,samples=len(flight),initial=flight[0],final=flight[-1]))
    finally:game.close()
    paths=[Path(__file__),source,model,model.with_suffix('.h'),core/'interp816.h',runtime,ROOT/'tools/md_lab.py',trace,
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'.tools/genesis-plus-gx/core/m68k/m68k.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,fixtures=cases,natural=natural,compile_command=cmd,
                original_rom_instructions_modified=False,synthetic_cpu_fixtures=True,animation_displacement_intercepted=True,
                native_division_bus='16-bit dividend / 8-bit divisor at4204..4206; immediate quotient at4214..4215; original CPU delay NOPs execute',
                native_intercepts=['C196BC draw flags','C0AF09 supplied animation dx','C0CC61 spawn','C0AC84 retire'],
                md_intercepts=['18F050 draw flags','002CE6 supplied animation dx','00218E spawn','00213E retire'],
                production_adapter_enabled=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'fixtures',len(cases),[k for k,v in checks.items() if not v][:15],flush=True)


if __name__=='__main__':main()
