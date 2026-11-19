"""Compare actual early floor-contact calls with the detached original CPU.

Run with embedded32 Python. No fixture writes or alternative floor arithmetic.
"""
import csv
import ctypes as C
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-grounded';prior=ROOT/'build/pride-default-grounding'
    oracle=json.loads((prior/'build-report.json').read_text())
    for name,sha in oracle['source_sha256'].items():
        if name=='tools/audit_pride_default_grounding.py':
            if digest(ROOT/name)!=sha:assert digest(prior/'source-revisions'/(sha+'.py'))==sha
        else:assert digest(ROOT/name)==sha,name
    dll_dir=os.add_dll_directory('C:/mingw32/bin');dll=prior/'original-grounding.dll'
    assert digest(dll)==oracle['oracle_sha256'];library=C.CDLL(str(dll))
    library.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    rom=ROOT/'Lion King, The (USA).sfc'
    assert digest(rom)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert library.terrain_native_init(rom.read_bytes(),0x300000)
    library.grounding_snapshot_run.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_uint),C.c_void_p,C.POINTER(C.c_uint),C.c_void_p,C.c_void_p]
    cases={};sources={}
    for width in (256,320):
        for graphics in ('native','frames','palette','all'):
            for mode in ('aot','lle'):
                name=f'default/{width}-{graphics}-{mode}';folder=base/name
                report=folder/'report.json';r=json.loads(report.read_text());assert r['exit_code']==0
                sources[str(report.relative_to(ROOT)).replace('\\','/')]=digest(report)
                fields=('a','x','y','stack','direct_page','db','p','emulation')
                entry=next(csv.DictReader((folder/'ground-entry.csv').open()))
                returned=next(csv.DictReader((folder/'ground-return.csv').open()))
                abi=[int(entry[k]) for k in fields];expected=[int(returned[k]) for k in fields]
                assert int(entry['age'])==int(returned['age'])==268
                assert abi[3:8]==[0x2fc,0,0x7e,0x16,0]
                before=(folder/'ground-entry.bin').read_bytes();after=(folder/'ground-return.bin').read_bytes()
                output=C.create_string_buffer(0x20000);reads=C.create_string_buffer(0x20000);writes=C.create_string_buffer(0x20000);result=(C.c_uint*11)()
                assert library.grounding_snapshot_run(before,len(before),(C.c_uint*8)(*abi),output,result,reads,writes),list(result)
                assert output.raw==after,(name,'complete original RAM result')
                assert list(result)[:8]==expected,(name,list(result),expected)
                assert result[8:11]==[144,0,0xc087fe]
                assert int.from_bytes(before[0xb21d:0xb21f],'little')==1248
                assert int.from_bytes(after[0xb21d:0xb21f],'little')==1255
                for file in ('ground-entry.csv','ground-entry.bin','ground-return.csv','ground-return.bin'):
                    assert digest(folder/file)==r['artifacts_sha256'][file]
                cases[name]=dict(original_instructions=result[8],invalid_bus_accesses=result[9],
                    full_ram_and_registers_exact=True,return_pc='C087FE',stack_before=abi[3],stack_after=expected[3])
    sources.update({str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),dll,rom,prior/'build-report.json')})
    (base/'ground-cpu-report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,cases=cases,
        source_sha256=sources,full_first_level_fidelity_complete=False),indent=2)+'\n')
    dll_dir.close();print('Sixteen early floor-contact calls: full original CPU RAM/registers exact PASS',flush=True)


if __name__=='__main__':main()
