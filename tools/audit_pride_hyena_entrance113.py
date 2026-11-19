"""Original entrance decision differences: camera window and timer-zero handling."""
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

out=ROOT/'build/pride-hyena-entrance113';out.mkdir()
reference=ROOT/'build/pride-hyena-intro109/report.json';assert bound(reference)['result']=='ORIGINAL_HYENA_INTRO_CAPTURED'
source=ROOT/'tools/pride_hyena_entrance_oracle113.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(runtime),'-o',str(out/'oracle.dll')]
subprocess.run(command,check=True)
snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint];assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
native.hyena_entrance113.argtypes=[C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
cpu=Prefix.in_dll(game.core,'m68k')
def word(at,value=None):
    at&=65535
    if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
    game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
def pointer(at,value):word(at,value>>16);word(at+2,value)
def md_gate(v):
    rx,ry,px,py,timer=v
    pointer(0x81c4,0xff98ce);pointer(0xcd46,0xff9300);word(0xcd36,0x9400)
    word(0x98d6,1536);word(0x98d8,512);word(0x98ce+0x2c,timer)
    word(0x9308,px);word(0x930a,py);word(0x9408,1536-rx);word(0x940a,512-ry)
    cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
    for reg in range(16):game.core.m68k_set_reg(reg,0)
    for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19b5ea)]:game.core.m68k_set_reg(reg,value)
    for n in range(4096):
        pc=game.core.m68k_get_reg(16)&0xffffff
        if pc in (0x19b60e,0x19b690,0x19b6be):break
        game.core.m68k_run(cpu.cycles+1)
    else:raise AssertionError(('MD timeout',hex(pc)))
    choice=1 if pc==0x19b60e else 2 if pc==0x19b690 else 0
    sp=game.core.m68k_get_reg(15);assert sp==(0xfffcfe if choice else 0xfffd00)
    if choice:assert word(sp)==134
    return [choice,word(0x98ce+0x2c)]
xs=[-65,-64,-63,0,255,319,320,383,384,385,447,448];ys=[-65,-64,-63,0,287,288,289]
count=0;groups=dict(equal=0,timer_zero_underflow=0,camera_window=0,unexplained=0);examples=[]
try:
    with (out/'cases.jsonl').open('w') as log:
        for v in itertools.product(xs,ys,(1487,1488),(0,340,341,512,513,900),(0,1,2,60,65535)):
            args=(C.c_uint*5)(*(x&65535 for x in v));raw=(C.c_uint*2)();assert native.hyena_entrance113(args,raw),v
            other=md_gate(v);a=list(raw);rx,ry,px,py,timer=v
            if a==other:kind='equal'
            elif timer==0 and a==[2,0] and other==[0,65535]:kind='timer_zero_underflow'
            elif 320<=rx<384 and -64<ry<288 and py>512 and timer!=0:kind='camera_window'
            else:kind='unexplained'
            groups[kind]+=1;count+=1;row=dict(relative_x=rx,relative_y=ry,player_x=px,player_y=py,timer=timer,snes=a,md=other,kind=kind)
            log.write(json.dumps(row,separators=(',',':'))+'\n')
            if kind not in ('equal',) and len(examples)<12:examples.append(row)
finally:game.close()
checks=dict(all10080_cases=count==len(xs)*len(ys)*2*6*5,no_unexplained_differences=groups['unexplained']==0,
    both_differences_observed=groups['timer_zero_underflow']>0 and groups['camera_window']>0)
paths=[Path(__file__),reference,source,ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='ENTRANCE_DIFFERENCES_CHARACTERIZED' if all(checks.values()) else 'FAIL',checks=checks,fixtures=count,groups=groups,examples=examples,command=command,
    scope='Original entrance slices C14418..C144E8 and19B5EA..19B6BE; execute complete original camera-window helpers. Native audio wait fixed0. Stop before native jump or MD music call; native outgoing jump X-4/Y-2 checked, MD music argument134 checked. No audio callee/action execution or natural reachability claim.',production_changed=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Entrance',checks,count,groups,examples[:2],flush=True)
