"""Execute both originals at the first observed live countdown divergence."""
import argparse
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab
ap=argparse.ArgumentParser();ap.add_argument('--capture',default='build/pride-hyena-entrance157-drop/report.json');args=ap.parse_args()
reference=(ROOT/args.capture).resolve();capture=bound(reference);assert capture['result']=='CAPTURED' and all(capture['checks'].values())
difference_files=[p for p in reference.parent.glob('*-differences.json') if json.loads(p.read_text())];assert difference_files,'No live timer difference in this capture'
case=difference_files[0].name.removesuffix('-differences.json')
observed=capture['observations'];native={int(r['field']):r for r in observed[case+'-snes']};selected={int(r['field']):r for r in observed[case+'-md']}
common=sorted(native.keys()&selected.keys());first=next(f for f in common if native[f]['timer']!=selected[f]['timer']);previous=max(f for f in common if f<first)
keys=('x','y','camera_x','camera_y','player_x','player_y','timer');a=native[previous];b=selected[previous]
assert all(a[k]==b[k] for k in keys),(a,b)
v=[int(a[k]) for k in keys];assert v[-1]>0
proof=ROOT/'build/pride-hyena-countdown133/report.json';pr=bound(proof);assert pr['result']=='PASS'
dllpath=proof.parent/'oracle.dll';assert digest(dllpath)==pr['artifacts_sha256']['oracle.dll']
rompath=ROOT/'Lion King, The (USA).sfc';rom=read_rom(rompath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
oracle=C.CDLL(str(dllpath));oracle.terrain_native_init.argtypes=[C.c_void_p,C.c_uint];assert oracle.terrain_native_init(C.create_string_buffer(rom),len(rom))
oracle.entrance_countdown133.argtypes=[C.POINTER(C.c_uint),C.c_uint,C.POINTER(C.c_uint)]
results=[]
for source in (0,1):
    raw=(C.c_uint*3)();assert oracle.entrance_countdown133((C.c_uint*7)(*v),source,raw);results.append(list(raw))
game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
cpu=Prefix.in_dll(game.core,'m68k')
def word(at,value=None):
    at&=65535
    if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
    game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
def pointer(at,value):word(at,value>>16);word(at+2,value)
try:
    x,y,cx,cy,px,py,timer=v
    pointer(0x81c4,0xff98ce);pointer(0xcd46,0xff9300);word(0xcd36,0x9400)
    for at,value in [(0x98d6,x),(0x98d8,y),(0x98fa,timer),(0x9308,px),(0x930a,py),(0x9408,cx),(0x940a,cy)]:word(at,value)
    cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
    for reg in range(16):game.core.m68k_set_reg(reg,0)
    for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19b5ea)]:game.core.m68k_set_reg(reg,value)
    for n in range(4096):
        pc=game.core.m68k_get_reg(16)&0xffffff
        if pc in (0x19b60e,0x19b690,0x19b6be):break
        game.core.m68k_run(cpu.cycles+1)
    else:raise AssertionError('Original MD timeout')
    choice=1 if pc==0x19b60e else 2 if pc==0x19b690 else 0
    original_md=[choice,word(0x98fa)]
finally:game.close()
out=ROOT/'build/pride-hyena-entrance153-live-decision';out.mkdir()
checks=dict(actual_preceding_contexts_identical=True,positive_natural_timer=timer>0,
    native_original_result_matches_next_actual_timer=results[0][1]==int(native[first]['timer']),
    selected_adapter_result_matches_next_actual_timer=results[1][1]==int(selected[first]['timer']),
    selected_result_matches_complete_original_md_decision=results[1][:2]==original_md,
    original_window_difference_explains_actual_countdown=results[0][1]!=results[1][1] and results[1][2]==1)
mdpath=ROOT/'Lion King, The (World).md';assert digest(mdpath)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
paths=[Path(__file__),reference,*difference_files,proof,dllpath,rompath,mdpath,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,case=case,previous_field=previous,first_observed_timer_difference=first,input=v,
    original_snes=results[0],selected_adapter=results[1],original_md=original_md,actual_next=dict(snes=native[first],md=selected[first]),
    scope='First actual actor countdown difference after identical naturally reached pre-call geometry/player/timer. Complete original SNES decision with unchanged/selected maintained adapter and unmodified MD decision slice; stop before jump/music callees, native audio wait0. No full original-MD trajectory or audible-onset claim. Production/LLE replay still separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,'fields',previous,first,'original timers',results[0][1],original_md[1],flush=True)
