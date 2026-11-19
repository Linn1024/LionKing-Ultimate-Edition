"""Original full camera-window helpers at actual ordinary MD entrance coordinates."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab
from pride_arena_history import bound

out=ROOT/'build/pride-hyena-camera116';out.mkdir()
reference=ROOT/'build/pride-hyena-camera115/report.json';assert bound(reference)['result']=='ORIGINAL_HYENA_CAMERA_CAPTURED'
frames_path=reference.parent/'frames.json';frames=json.loads(frames_path.read_text());rows=[r for r in frames if r['action']==0x19b59e]
source=ROOT/'tools/pride_hyena_camera_oracle116.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(runtime),'-o',str(out/'oracle.dll')]
subprocess.run(command,check=True)
snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint];assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
native.hyena_camera116.argtypes=[C.c_uint]*4+[C.POINTER(C.c_uint)]
game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
cpu=Prefix.in_dll(game.core,'m68k')
def word(at,value):game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
def pointer(at,value):word(at,value>>16);word(at+2,value)
results=[];different=[]
try:
    for row in rows:
        raw=(C.c_uint*1)();assert native.hyena_camera116(row['x'],row['y'],row['camera_x'],row['camera_y'],raw)
        pointer(0x81c4,0xff98ce);word(0xcd36,0x9400);word(0x98d6,row['x']);word(0x98d8,row['y']);word(0x9408,row['camera_x']);word(0x940a,row['camera_y'])
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(15,0xfffd00),(16,0x1a7cc0)]:game.core.m68k_set_reg(reg,value)
        pointer(0xfd00,0x4000);word(0xfd04,64);word(0xfd06,64)
        for n in range(1024):
            if game.core.m68k_get_reg(16)&0xffffff==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError('MD helper timeout')
        assert game.core.m68k_get_reg(15)==0xfffd04
        other=game.core.m68k_get_reg(0)&65535
        actual=dict(field=row['field'],snes=raw[0],md=other,relative_x=row['relative_x'],relative_y=row['relative_y'],timer=row['timer'])
        results.append(actual)
        if raw[0]!=other:different.append(actual)
finally:game.close()
(out/'cases.json').write_text(json.dumps(results,indent=2)+'\n')
by_field={r['field']:r for r in frames};decrements=[]
for row in different:
    ref=by_field[row['field']];previous=by_field.get(row['field']-1)
    if previous and ref['timer']==previous['timer']-1 and 320<=previous['relative_x']<384:
        decrements.append(row)
checks=dict(all251_waiting_coordinates=len(rows)==251,original_helpers_show_width_difference=bool(different),
    all_differences_md_only_right_band=all(r['snes']==0 and r['md']==65535 and 320<=r['relative_x']<384 and -64<r['relative_y']<288 for r in different),
    three_actual_countdown_updates_in_that_band=len(decrements)==3)
paths=[Path(__file__),reference,frames_path,source,ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='NATURAL_CAMERA_WINDOW_DIFFERENCE_VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,differences=different,confirmed_countdown_updates=decrements,
    scope='Complete untouched original helpers on identical recorded MD actor/camera coordinates,64-pixel margins. This proves a width difference at natural coordinates and three observed decrements while both adjacent camera samples lie in the MD-only band. Does not claim matched full SNES/MD trajectories or prove timer-zero reachability.',production_changed=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Natural camera window',checks,'differences',len(different),'decrement fields',[r['field'] for r in decrements],flush=True)
