"""Execute original shared enemy integration/gravity with matched incoming state.

No terrain/contact calls are intercepted. These helpers perform arithmetic only;
their callers' collision/AI/launch selection remain separate requirements.
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
from pride_arena_history import bound


def main():
    previous=ROOT/'build/pride-hyena-motion87/report.json';p=bound(previous)
    assert p['result']=='ORIGINAL_HYENA_MOTION_CAPTURED' and all(p['checks'].values())
    out=ROOT/'build/pride-enemy-motion88';out.mkdir()
    source=ROOT/'tools/pride_enemy_motion_oracle88.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c';headers=ROOT/'engine/snesrecomp/runner/src/snes'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.motion_native88.argtypes=[C.c_uint]*7+[C.POINTER(C.c_uint)]
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
    def call(pc):
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(15,0xfffd00),(16,pc)]:game.core.m68k_set_reg(reg,value)
        longword(0xfd00,0x4000)
        for n in range(2048):
            current=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==current
            if current==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD helper timeout',hex(pc),hex(current)))
        assert game.core.m68k_get_reg(15)==0xfffd04
    def md_run(mode,x,y,xf,yf,vx,vy):
        actor=0x98ce
        for a in range(actor,actor+128,2):word(a,0)
        longword(0x81c4,0xff0000|actor)
        for offset,value in [(8,x),(10,y),(0x34,xf),(0x36,yf)]:word(actor+offset,value)
        longword(actor+0x38,vx);longword(actor+0x3c,vy)
        if mode:call(0x18ed84)
        call(0x1a0074)
        return [word(actor+8),word(actor+10),word(actor+0x34),word(actor+0x36),longword(actor+0x38),longword(actor+0x3c)]
    fixtures=[]
    velocities=[-8*65536,-5*65536,-2*65536,-1,0,0x68000,0x70000,0x70001,0x80000]
    for (x,y),(xf,yf),vx,vy in itertools.product([(1024,256),(1458,341)],[(0,0),(32768,32768),(65535,65535)],[-4*65536,0,4*65536],velocities):
        fixtures.append((x,y,xf,yf,vx,vy,'normal-domain-grid'))
    observed=set();paths=[Path(__file__),previous,source,ROOT/'tools/pride_terrain_native_oracle.c',runtime]
    for name in p['cases']:
        a,b=name.split('-');file=previous.parent/a/b/'frames.json';paths.append(file)
        for row in json.loads(file.read_text()):observed.add((row['x'],row['y'],0,0,row['vx_q16'],row['vy_q16']))
    fixtures += [(*row,'observed_integer_velocity_with_zero_fraction') for row in sorted(observed)]
    failures=[];count=0
    try:
        with (out/'cases.jsonl').open('w') as log:
            for mode in (0,1):
                for x,y,xf,yf,vx,vy,origin in fixtures:
                    raw=(C.c_uint*6)();values=(mode,x,y,xf,yf,vx&0xffffffff,vy&0xffffffff)
                    assert native.motion_native88(*values,raw)
                    other=md_run(*values);equal=list(raw)==other;count+=1
                    row=dict(mode=mode,input=list(values[1:]),origin=origin,snes=list(raw),md=other,equal=equal)
                    log.write(json.dumps(row,separators=(',',':'))+'\n')
                    if not equal:failures.append(row)
    finally:game.close()
    checks=dict(all_matched_helper_outputs_equal=not failures,grid_and_observed_inputs_executed=count==2*len(fixtures),
                original87_capture_bound=True)
    paths += [snespath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='SHARED_ENEMY_MOTION_VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,fixture_count=count,
                unique_observed_integer_velocity_inputs=len(observed),failures=failures,
                native_helpers=['C1954C','C16F89'],md_helpers=['18ED84','1A0074'],command=command,
                complete_original_helpers=True,callee_interception=False,guest_or_rom_production_edits=False,
                runtime_or_capabilities_changed=False,
                scope='Matched arithmetic for integration alone and gravity-plus-integration. Observed states supply integer/velocity inputs with synthetic zero fractions. Does not prove launch decisions, collision, animations, action interruptions or whole AI.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],count,'fixtures',checks,flush=True)


if __name__=='__main__':main()
