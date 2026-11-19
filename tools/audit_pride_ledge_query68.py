"""Compare untouched original ledge queries; use the embedded32-bit Python."""
import argparse
import ctypes as C
import importlib.util
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
from md_lab import MdLab


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True);ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args();out=ROOT/args.out;out.mkdir()
    source=ROOT/'tools/pride_ledge_query_oracle68.c'
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    headers=ROOT/'engine/snesrecomp/runner/src/snes'
    for p in (Path(__file__),source):shutil.copy2(p,out/p.name)
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';mdpath=ROOT/'Lion King, The (World).md'
    snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom(mdpath.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    spec=importlib.util.spec_from_file_location('ledge68_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    sp=lambda k:int.from_bytes(snes[0x387+k:0x38a+k],'little')&0x3fffff
    mp=lambda k:struct.unpack_from('>I',md,0x1cfdb4+k)[0]
    table=lz.decompress(snes,sp(0))[0];sm=lz.decompress(snes,sp(9))[0];mm=lz.decompress(md,mp(16))[0]
    native_tags={table[(struct.unpack_from('<H',sm,i)[0]&0xfff8)//2+2] for i in range(0,len(sm),2)}
    md_tags={md[mp(4)+(struct.unpack_from('>H',mm,i)[0]&0xfff8)//2+2] for i in range(0,len(mm),2)}
    pride_tags=native_tags|md_tags
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.ledge_native.argtypes=[C.c_uint]*4+[C.POINTER(C.c_uint)]
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
    word(0xcd1e,16);pointer(0xcd22,0xffe000);pointer(0xcd2e,0xffe100)
    pointer(0x81c4,0xff93ce);word(0x93ce+12,0x9400);pointer(0x9400+10,0xffe600)
    word(0xe600+20,0);word(0xe600+22,0)
    def md_run(facing,tag,neighbor):
        word(0xe000+32+4,8);word(0xe000+32+(6 if facing else 2),16)
        word(0xe000+32+(2 if facing else 6),0)
        game.work_ram[0xe106^1]=tag;game.work_ram[0xe10a^1]=neighbor
        game.work_ram[(0x9400+8)^1]=8 if facing else 0
        for at,value in [(0xe300,0xa55a),(0xe304,0x5aa5),(0xe308,0xc33c)]:word(at,value)
        game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(15,0xfffd00),(16,0x26d4)]:game.core.m68k_set_reg(reg,value)
        pointer(0xfd00,0x4000);word(0xfd04,40);word(0xfd06,40)
        for at,value in [(0xfd08,0xffe300),(0xfd0c,0xffe304),(0xfd10,0xffe308)]:pointer(at,value)
        for n in range(1024):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc==0x4000:break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('MD return timeout',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xfffd04
        return [game.core.m68k_get_reg(0)&65535,word(0xe300),word(0xe304),word(0xe308)]
    domain=(0,0xad,0xae,0xaf,0xea,0xfd,0xfe,0xff) if args.pilot else range(256)
    groups={};examples=[];count=0
    try:
        for facing,tag,neighbor,timer in itertools.product((0,1),domain,domain,(0,16)):
            result=(C.c_uint*7)();assert native.ledge_native(facing,tag,neighbor,timer,result)
            other=md_run(facing,tag,neighbor);actual=[result[0],result[2],result[3],result[4]]
            assert result[0]==result[1]
            same=actual==other;key=f'{tag:02x}'
            group=groups.setdefault(key,dict(cases=0,differences=0,pride_pairs=0,pride_differences=0))
            group['cases']+=1;group['differences']+=not same
            if tag in pride_tags and neighbor in pride_tags:
                group['pride_pairs']+=1;group['pride_differences']+=not same
            if not same and len(examples)<64:examples.append(dict(facing=facing,tag=tag,neighbor=neighbor,timer=timer,snes=list(result),md=other))
            count+=1
    finally:game.close()
    checks=dict(expected_cases=count==len(domain)**2*4,pride_tag_pairs_exercised=any(g['pride_pairs'] for g in groups.values()),
                authored_pride_tag_pairs_agree=not any(g['pride_differences'] for g in groups.values()))
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',ROOT/'tools/md_lab.py',ROOT/'engine/tools/re/decompress.py',snespath,mdpath,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'DIFFERENCE',checks=checks,cases=count,pilot=args.pilot,groups=groups,first_differences=examples,
                differences=sum(g['differences'] for g in groups.values()),pride_differences=sum(g['pride_differences'] for g in groups.values()),
                snes_authored_tags=sorted(native_tags),md_authored_tags=sorted(md_tags),
                native_entry='C0C855',md_entry='0026D4',production_modified=False,
                scope='Full original ledge query, synthetic x40/y40 zero pose offsets; both facing directions, all current/adjacent tag pairs, native timer0/16. Authored tags are an inventory, not proof of reachable tag adjacency or full actor movement.',
                command=command,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],count,'differences',report['differences'],'authored Pride',report['pride_differences'],examples[:2],flush=True)


if __name__=='__main__':main()
