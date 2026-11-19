"""Bounded original-CPU evidence for C1A8C8's two adult-pose setters.

Run using .tools/python32/python.exe. Synthetic actor fixtures prove callback
selection, not ordinary Pride reachability. Keep all production fallbacks.
"""
import ctypes as C
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-ambiguous-caller')
    args=parser.parse_args()
    out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build')
    out.mkdir()  # Preserve an earlier run rather than overwrite its evidence.
    source=ROOT/'tools/pride_ambiguous_caller_oracle.c'
    interpreter=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    library=out/'oracle.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',
             '-I',str(ROOT/'engine/snesrecomp/runner/src/snes'),
             str(source),str(interpreter),'-o',str(library)]
    subprocess.run(command,check=True,cwd=ROOT)
    rom=read_rom('Lion King, The (USA).sfc',
        '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    dll=C.CDLL(str(library))
    dll.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert dll.terrain_native_init(C.create_string_buffer(rom),len(rom))
    dll.ambiguous_caller_run.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    result=(C.c_uint*5)()
    cases=[]
    # All calls execute from the original entry, including its real DP frame.
    # Stop before animation/update functions: their lifetime is separate scope.
    for name,current_action,flag,count,stop,expected in (
        ('initial-flag-set',0,0x40,0,0xc0fac4,0xc0e366),
        ('initial-flag-clear',0,0,0,0xc0af09,0xc0e5a6),
        ('continuation-count-one',0xc1a8c8,0,1,0xc1a9dc,0xc0e366)):
        snapshot=bytearray(0x20000)
        def w(at,value):struct.pack_into('<H',snapshot,at,value)
        actor=0xb213;render=0xe100
        w(0x68,actor);w(0xa68c,0x1000);w(actor+12,render)
        w(render+8,flag);w(actor+0x2c,count)
        snapshot[actor+0x30:actor+0x33]=current_action.to_bytes(3,'little')
        steps=set()
        for age in range(65536):
            w(0x2000,age)
            assert dll.ambiguous_caller_run(C.create_string_buffer(bytes(snapshot)),
                len(snapshot),stop,result),(name,age,list(result))
            stack=0x1fed if stop==0xc1a9dc else 0x1fea
            assert result[0]==stop and result[1]==expected and result[2]==stack,(
                name,age,list(result))
            steps.add(result[3])
        cases.append(dict(name=name,age_cases=65536,callback=hex(expected),
                          stop_before=hex(stop),instruction_counts=sorted(steps),
                          stack=hex(stack),unmapped_bus_accesses=0))
    # Exact original instructions bind the two stores and the only literal
    # JSL caller. These are source references, not a global control-flow proof.
    assert rom[0x1a92e:0x1a931]==bytes.fromhex('a966e3')
    assert rom[0x1a9b7:0x1a9ba]==bytes.fromhex('a966e3')
    needle=bytes.fromhex('22c8a8c1')
    callers=[0xc00000+i for i in range(len(rom)) if rom.startswith(needle,i)]
    assert callers==[0xc1aaff]
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',interpreter,library]
    report=dict(result='BOUNDED_CALLBACK_SELECTION_PASS',original_cpu_cases=196608,
        cases=cases,literal_jsl_callers=[hex(v) for v in callers],
        cub_age_can_select_adult_callback=True,production_mappings_unchanged=True,
        ordinary_pride_reachability_proven=False,global_indirect_scope_closed=False,
        next_action='Trace installation and scene ownership of C1AAF0/C1A8C8; do not exclude by age.',
        compiler_command=command,rom_sha256=hashlib.sha256(rom).hexdigest(),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],report['original_cpu_cases'],'original CPU cases',flush=True)


if __name__=='__main__':main()
