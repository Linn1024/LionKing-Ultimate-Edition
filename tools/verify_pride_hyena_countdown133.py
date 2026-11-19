"""Full original entrance decisions at recorded coordinates and positive timers.

Audio callees and jump actions are deliberately outside the slice. This does
not claim a full player trajectory or change the current release candidate.
"""
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
    out=ROOT/'build/pride-hyena-countdown133';out.mkdir()
    references=[ROOT/'build'/name/'report.json' for name in ('pride-hyena-entrance132','pride-hyena-camera115','pride-hyena-entrance114')]
    for p in references:assert all(bound(p)['checks'].values()),p
    frames_path=ROOT/'build/pride-hyena-camera115/frames.json'
    rows=[r for r in json.loads(frames_path.read_text()) if r['action']==0x19b59e]
    source=Path(__file__).with_name('pride_hyena_countdown_oracle133.c')
    module=ROOT/'engine/runner/tlk_hyena_entrance.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    includes=['-I'+str(ROOT/p) for p in ('engine/runner','engine/snesrecomp/runner/src','engine/snesrecomp/runner/src/snes')]
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',*includes,str(source),str(module),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    native.entrance_countdown133.argtypes=[C.POINTER(C.c_uint),C.c_uint,C.POINTER(C.c_uint)]
    # Independent unmodified original-SNES decision slice from113.
    original_path=ROOT/'build/pride-hyena-entrance113/report.json';original=bound(original_path)
    oracle_path=original_path.parent/'oracle.dll';assert digest(oracle_path)==original['artifacts_sha256']['oracle.dll']
    baseline=C.CDLL(str(oracle_path));baseline.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert baseline.terrain_native_init(C.create_string_buffer(snes),len(snes))
    baseline.hyena_entrance113.argtypes=[C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
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
        x,y,cx,cy,px,py,timer=v
        pointer(0x81c4,0xff98ce);pointer(0xcd46,0xff9300);word(0xcd36,0x9400)
        word(0x98d6,x);word(0x98d8,y);word(0x98fa,timer)
        word(0x9308,px);word(0x930a,py);word(0x9408,cx);word(0x940a,cy)
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
        return [choice,word(0x98fa)]
    total=hits=differences=0;failures=[]
    try:
        with (out/'cases.jsonl').open('w') as log:
            for row in rows:
                for timer in range(1,61):
                    v=[row[k] for k in ('x','y','camera_x','camera_y','player_x','player_y')]+[timer]
                    args=(C.c_uint*7)(*v);results=[]
                    for selected in (0,1):
                        raw=(C.c_uint*3)();assert native.entrance_countdown133(args,selected,raw),(row['field'],timer,selected)
                        results.append(list(raw));hits+=raw[2]
                    # Original113 uses translated coordinates. Translation preserves
                    # the helper geometry, horizontal player predicate and y relation.
                    bv=[v[0]-v[2],v[1]-v[3],v[4]+1536-v[0],v[5]+512-v[1],timer]
                    orig=(C.c_uint*2)();assert baseline.hyena_entrance113((C.c_uint*5)(*(x&65535 for x in bv)),orig)
                    md=md_gate(v);ok=results[0][:2]==list(orig) and results[1][:2]==md
                    actual=dict(field=row['field'],timer=timer,native=results[0],selected=results[1],original_snes=list(orig),original_md=md,matched=ok)
                    log.write(json.dumps(actual,separators=(',',':'))+'\n')
                    if not ok and len(failures)<12:failures.append(actual)
                    differences+=results[0][:2]!=md;total+=1
    finally:game.close()
    checks=dict(all15060_positive_timer_cases=total==251*60,native_original_decisions_preserved=not failures,
                selected_original_md_decisions_matched=not failures,actual_operand_adjustments=hits>0,original_width_changes_countdown=differences>0)
    paths=[Path(__file__),source,module,*references,frames_path,original_path,oracle_path,runtime,snespath,mdpath,
           ROOT/'tools/pride_hyena_entrance_adapter132.c',ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,fixtures=total,adjustments=hits,decision_differences=differences,failures=failures,command=command,
        scope='Original entrance decision slices and complete camera helpers at251 natural coordinate sets x positive timers1..60. Native audio wait0. Stops before actual jump/music callees. Maintained unlinked operand adapter; no player trajectory/menu/source-switch or audible timing claim.',
        player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,total,hits,differences,failures[:1],flush=True)
if __name__=='__main__':main()
