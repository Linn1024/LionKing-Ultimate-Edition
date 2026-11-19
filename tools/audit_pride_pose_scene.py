"""Trace original scene-loader ownership of the ambiguous C1AAF0 caller.

Synthetic isolated CPU fixtures establish loader/dispatch/installation paths.
They do not establish global indirect unreachability or ordinary completion.
Run with .tools/python32/python.exe; outputs are local research evidence.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom,NAMES


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-pose-scene')
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build')
    out.mkdir()
    source=ROOT/'tools/pride_pose_scene_oracle.c'
    interpreter=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    library=out/'oracle.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I',
        str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(interpreter),'-o',str(library)]
    subprocess.run(command,check=True,cwd=ROOT)
    rom=read_rom('Lion King, The (USA).sfc',
        '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    dll=C.CDLL(str(library));dll.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert dll.terrain_native_init(C.create_string_buffer(rom),len(rom))
    dll.pose_scene_run.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    result=(C.c_uint*4)();executions=[]
    w=lambda ram,at,value:struct.pack_into('<H',ram,at,value)
    u16=lambda ram,at:struct.unpack_from('<H',ram,at)[0]
    u24=lambda ram,at:int.from_bytes(ram[at:at+3],'little')
    def run(ram,entry,stop,index=1):
        buf=(C.c_ubyte*len(ram)).from_buffer(ram)
        assert dll.pose_scene_run(buf,len(ram),entry,stop,index,result),(hex(entry),list(result))
        executions.append(dict(entry=hex(entry),stop=hex(stop),instructions=result[2],
            stack=hex(result[1]),unmapped_accesses=result[3]))
    def fresh():
        ram=bytearray(0x20000)
        w(ram,0x7a,0xe000)  # Original free object pool, consumed by C0AAFD.
        return ram
    rows=[]
    for level in list(range(10))+['pride-boss']:
        descriptor=u24(rom,0x357+level*3) if isinstance(level,int) else 0xc0080d
        pointer=u24(rom,(descriptor&0x3fffff)+43)
        callback=u24(rom,pointer&0x3fffff) if pointer else 0
        ram=fresh();ram[0xdf:0xe2]=descriptor.to_bytes(3,'little')
        run(ram,0xc086dc,0xc086ec)
        if pointer:
            assert u16(ram,0x68)==u16(ram,0x76)==0xe000
            assert u24(ram,0xe004)==pointer
            run(ram,0xc0abbb,callback)
            assert u16(ram,0x68)==0xe000
        else:
            assert u16(ram,0x76)==0
        rows.append(dict(level=level,name=NAMES[level] if isinstance(level,int) else 'Pride boss variant',
            descriptor=hex(descriptor),script_pointer=hex(pointer),dispatched_callback=hex(callback)))
    assert rows[0]['dispatched_callback']==rows[-1]['dispatched_callback']=='0xc0d0f8'
    assert rows[6]['dispatched_callback']=='0xc0d3ce'
    # Trigger the Destiny script's actual boundary; prove its store rather than
    # treating an immediate byte match as a complete installation path.
    boundaries=[]
    for x,y,velocity,selected in [(0,0x28b,0,True),(0x124,0x28b,0,True),
            (0x125,0x28b,0,False),(0,0x28a,0,False),(0,0x28b,1,False)]:
        ram=fresh();actor=0xb213;w(ram,0x6e,actor)
        w(ram,actor+8,x);w(ram,actor+10,y);w(ram,actor+0x3c,velocity)
        run(ram,0xc0d3ce,0xc0d404)
        action=u24(ram,actor+0x30)
        assert action==(0xc1aaf0 if selected else 0)
        boundaries.append(dict(x=x,y=y,velocity=velocity,action=hex(action)))
        if selected:
            w(ram,0x68,actor);w(ram,0xa68c,0x1000);w(ram,actor+12,0xe100)
            w(ram,0xe108,0x40)
            run(ram,action,0xc0fac4,0)
            assert u24(ram,actor+14)==0xc0e366
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',interpreter,library]
    report=dict(result='ORIGINAL_SCENE_PATHS_PASS',scene_loaders=rows,
        destiny_trigger_boundaries=boundaries,original_cpu_executions=executions,
        pride_loader_callback='0xc0d0f8',destiny_loader_callback='0xc0d3ce',
        destiny_installs_ambiguous_action=True,global_indirect_unreachability_proven=False,
        ordinary_play_or_full_lifetime_proven=False,production_mappings_unchanged=True,
        rom_sha256=hashlib.sha256(rom).hexdigest(),compiler_command=command,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(executions),'CPU executions; Pride and Destiny paths distinguished',flush=True)


if __name__=='__main__':main()
