"""Execute original contact geometry on Pride header shapes and edge cases.

Same bounds are encoded in each original layout: this isolates geometry rules
from the independently selectable pose-header differences. Embedded32-bit Python.
"""
import argparse
import ctypes as C
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab


def oriented(box,flip):
    l,t,r,b=box
    return (-r if flip&1 else l,-b if flip&2 else t,-l if flip&1 else r,-t if flip&2 else b)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True)
    ap.add_argument('--pilot',action='store_true');args=ap.parse_args()
    out=ROOT/args.out;out.mkdir()
    source=ROOT/'tools/pride_body_overlap_oracle69.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    headers=ROOT/'engine/snesrecomp/runner/src/snes'
    for p in (Path(__file__),source):shutil.copy2(p,out/p.name)
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    coverage_path=ROOT/'build/pride-action-art-current/report.json';coverage=bound(coverage_path)
    npc_path=ROOT/'tools/pride_npc_pairs.json';npc=json.loads(npc_path.read_text())['pairs']
    cub_poses={p['md'] for v in coverage['observations'].values() for p in v['coverage']['seen_cub_poses']}
    cub_shapes={struct.unpack_from('>4h',md,p+12) for p in cub_poses}
    enemies={}
    for row in npc:
        if row['role'] in ('hyena','lizard','porcupine'):
            p=int(row['md'],16);shape=struct.unpack_from('>4h',md,p+12)
            enemies.setdefault(shape,set()).add(row['role'])
    player_shapes=sorted(cub_shapes);enemy_shapes=sorted(enemies)
    if args.pilot:player_shapes=player_shapes[:2];enemy_shapes=enemy_shapes[:2]
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.body_native69.argtypes=[C.POINTER(C.c_int16)]*2+[C.c_uint]*3+[C.POINTER(C.c_uint)]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):_fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value):word(at,value>>16);word(at+2,value)
    C.memset(C.addressof(game.work_ram),0,65536)
    pointer(0x81c4,0xff944e)
    for actor,draw,pose in ((0x93ce,0x9600,0xe400),(0x944e,0x9640,0xe440)):
        word(actor+12,draw);pointer(draw+10,0xff0000|pose)
    word(0x93ce+8,1024);word(0x93ce+10,1024)
    def md_run(flips,x,y):
        word(0x944e+8,x);word(0x944e+10,y)
        for k,draw in enumerate((0x9600,0x9640)):
            game.work_ram[(draw+8)^1]=((8 if flips>>(2*k)&1 else 0)|(16 if flips>>(2*k)&2 else 0))
        # Independent calls have no outer display loop to renormalize the
        # signed core clock. Start each synthetic CPU fixture at time zero.
        cpu.cycles=0;cpu.refresh=0;cpu.end=0
        game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in ((17,0x2700),(15,0xfffd00),(16,0x18d594)):game.core.m68k_set_reg(reg,value)
        pointer(0xfd00,0x4000);pointer(0xfd04,0xff93ce)
        for n in range(256):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD helper timeout',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xfffd04
        return game.core.m68k_get_reg(0)&65535
    count=0;failures=[];blocked=0;outcomes=hashlib.sha256()
    try:
        for p,e in itertools.product(player_shapes,enemy_shapes):
            pb=(C.c_int16*4)(*p);eb=(C.c_int16*4)(*e)
            for pose,shape in ((0xe400,p),(0xe440,e)):
                for c,value in enumerate(shape):word(pose+12+c*2,value&65535)
            for flips in range(16):
                player=tuple(v+1024 for v in oriented(p,flips&3));other=oriented(e,flips>>2)
                xs=[player[0]-other[2]-1,player[0]-other[2],1024,player[2]-other[0],player[2]-other[0]+1]
                ys=[player[1]-other[3]-1,player[1]-other[3],1024,player[3]-other[1],player[3]-other[1]+1]
                for x,y in itertools.product(xs,ys):
                    result=(C.c_uint*5)();assert native.body_native69(pb,eb,flips,x,y,result)
                    md_result=md_run(flips,x,y)
                    expected=65535 if x+other[2]>=player[0] and y+other[3]>=player[1] and x+other[0]<=player[2] and y+other[1]<=player[3] else 0
                    same=result[0]==md_result==expected and list(result[1:])==list(player)
                    if not same and len(failures)<64:failures.append(dict(player_shape=p,enemy_shape=e,flips=flips,x=x,y=y,native=list(result),md=md_result,expected=expected,player_bounds=player))
                    count+=1;blocked+=bool(expected);outcomes.update(struct.pack('<7H',flips,x,y,result[0],md_result,expected,int(same)))
    except BaseException as exc:
        (out/'failure.json').write_text(json.dumps(dict(result='INCOMPLETE',error=repr(exc),completed=count,
            cycles=cpu.cycles,pc=game.core.m68k_get_reg(16),sp=game.core.m68k_get_reg(15),
            player_shape=p,enemy_shape=e,flips=flips,x=x,y=y),indent=2)+'\n')
        raise
    finally:game.close()
    checks=dict(full_domain=count==len(player_shapes)*len(enemy_shapes)*16*25,original_helpers_match_expected_inclusive_geometry=not failures,
                both_contact_and_separation_exercised=0<blocked<count)
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',ROOT/'tools/md_lab.py',coverage_path,npc_path,snespath,mdpath,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,pilot=args.pilot,cases=count,contact_cases=blocked,
                observed_cub_poses=len(cub_poses),player_shapes=player_shapes,enemy_shapes=[dict(bounds=b,roles=sorted(enemies[b])) for b in enemy_shapes],
                failures=failures,outcome_stream_sha256=outcomes.hexdigest(),production_modified=False,
                scope=__doc__,native_entries=['C0B468..C0B4F0 (cached bounds tail)','C0D512'],md_entry='18D594',
                natural_playthrough_or_full_combat_proven=False,command=command,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],count,'cases',len(player_shapes),'cub shapes',len(enemy_shapes),'enemy shapes','failures',len(failures),failures[:1],flush=True)


if __name__=='__main__':main()
