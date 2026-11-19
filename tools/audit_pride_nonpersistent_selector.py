"""Execute both original selectors and audit the complete Pride terrain tables."""
import ctypes as C
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab


def main():
    out=ROOT/'build/pride-nonpersistent-selector';out.mkdir()
    snes_path=ROOT/'Lion King, The (USA).sfc';md_path=ROOT/'Lion King, The (World).md'
    s=read_rom(snes_path.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom(md_path.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    helper=ROOT/'tools/pride_attribute_selector_oracle.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    headers=ROOT/'engine/snesrecomp/runner/src/snes'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),str(helper),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(cmd,check=True)
    lib=C.CDLL(str(out/'oracle.dll'));lib.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert lib.terrain_native_init(C.create_string_buffer(s),len(s))
    lib.pride_attribute_selector.argtypes=[C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    game=MdLab();game.core.m68k_run.argtypes=[C.c_uint]
    class Map(C.Structure):_fields_=[(k,C.c_void_p) for k in ('base','read8','read16','write8','write16')]
    class Prefix(C.Structure):
        _fields_=[('map',Map*256),('poll',C.c_uint*3),('cycles',C.c_int),('refresh',C.c_int),
                  ('end',C.c_uint),('dar',C.c_uint*16),('pc',C.c_uint)]
    cpu=Prefix.in_dll(game.core,'m68k')
    def word(at,value=None):
        at&=65535
        if value is None:return game.work_ram[at]|game.work_ram[at+1]<<8
        game.work_ram[at]=value&255;game.work_ram[at+1]=(value>>8)&255
    def pointer(at,value):word(at,value>>16);word(at+2,value)
    cases=[];checks={};native_by_input={}
    try:
        for attribute in range(256):
            for index in range(4):
                result=(C.c_uint*3)();assert lib.pride_attribute_selector(attribute,index,result)
                game.core.m68k_pulse_reset();actor=0x944e
                pointer(0x81c4,0xff0000|actor);game.work_ram[(actor+0x40)^1]=attribute
                for reg in range(16):game.core.m68k_set_reg(reg,0)
                for reg,value in [(17,0x2700),(15,0xffe000),(16,0x18e8e8)]:game.core.m68k_set_reg(reg,value)
                pointer(0xe000,0x4000);word(0xe004,index)
                for n in range(128):
                    if game.core.m68k_get_reg(16)&0xffffff==0x4000:break
                    game.core.m68k_run(cpu.cycles+1)
                else:raise AssertionError(('MD selector did not return',attribute,index))
                md=game.core.m68k_get_reg(0)&65535
                high=attribute>>4
                expected=0 if attribute&15!=index or attribute<0x50 else high-(4 if attribute<0xb0 else 10)
                checks[f'original-{attribute}-{index}']=result[0]==md==expected and game.core.m68k_get_reg(15)==0xffe004
                native_by_input[attribute,index]=result[0]
                cases.append(dict(attribute=attribute,index=index,native=list(result),md=md,md_steps=n,expected=expected))
    finally:game.close()
    spec=importlib.util.spec_from_file_location('pride_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    sp=lambda o:int.from_bytes(s[0x387+o:0x38a+o],'little')&0x3fffff
    mp=lambda o:int.from_bytes(m[0x1cfdb4+o:0x1cfdb8+o],'big')
    sc=lz.decompress(s,sp(0))[0];sm=lz.decompress(s,sp(9))[0]
    mc=m[mp(4):mp(8)];mm=lz.decompress(m,mp(16))[0]
    tables={}
    for label,mapping,dictionary,fmt in [('snes',sm,sc,'<H'),('md',mm,mc,'>H')]:
        assert len(mapping)==16000 and len(dictionary)%4==0
        attributes=[dictionary[i+2] for i in range(0,len(dictionary),4)]
        cells=[]
        for i in range(8000):
            word_value=struct.unpack_from(fmt,mapping,i*2)[0];at=(word_value&0xfff8)//2
            assert at+4<=len(dictionary)
            cells.append(dict(cell=i,attribute=dictionary[at+2]))
        candidates=[i for i,a in enumerate(attributes) if native_by_input[a,2]]
        cell_candidates=[r for r in cells if native_by_input[r['attribute'],2]]
        checks[label+'_all_dictionary_records_reject_index2']=not candidates
        checks[label+'_all8000_cells_reject_index2']=not cell_candidates
        tables[label]=dict(dictionary_bytes=len(dictionary),dictionary_records=len(attributes),
                           dictionary_sha256=__import__('hashlib').sha256(dictionary).hexdigest(),
                           map_sha256=__import__('hashlib').sha256(mapping).hexdigest(),
                           unique_attributes=sorted(set(attributes)),nonpersistent_dictionary_records=candidates,
                           nonpersistent_cells=cell_candidates)
    constructors=[]
    for label,rom,needle,width in [('snes',s,bytes.fromhex('22875bc1'),3),('md',m,bytes.fromhex('4eb90019a446'),4)]:
        at=0;sites=[]
        while True:
            at=rom.find(needle,at)
            if at<0:break
            before=rom[at-width:at]
            assert before[0]==(0xf4 if label=='snes' else 0x3f)
            value=int.from_bytes(before[-2:],'little' if label=='snes' else 'big')
            sites.append(dict(address=at+(0xc00000 if label=='snes' else 0),argument=value,bytes=(before+needle).hex()))
            at+=1
        constructors.append(dict(source=label,calls=sites))
        checks[label+'_four_direct_attack_calls']=len(sites)==4 and [r['argument'] for r in sites]==[1,1,0,1]
    paths=[Path(__file__),helper,ROOT/'tools/pride_terrain_native_oracle.c',runtime,headers/'interp816.h',
           ROOT/'tools/md_lab.py',ROOT/'engine/tools/re/decompress.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,tables=tables,
                direct_constructor_calls=constructors,compile_command=cmd,
                source_rom_sha256=dict(snes=digest(snes_path),md=digest(md_path)),
                synthetic_original_selector_calls=True,whole_dynamic_reachability_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),tables,flush=True)


if __name__=='__main__':main()
