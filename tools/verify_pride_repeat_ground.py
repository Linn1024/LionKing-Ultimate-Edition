"""Check both live grounding calls per run against detached original CPU execution."""
import csv
import ctypes as C
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from run_pride_repeat_matrix import CASES,WINDOWS,name


def main():
    base=ROOT/'build/pride-repeat';prior=ROOT/'build/pride-default-grounding';oracle=json.loads((prior/'build-report.json').read_text())
    for file,sha in oracle['source_sha256'].items():
        actual=ROOT/file
        if file=='tools/audit_pride_default_grounding.py' and digest(actual)!=sha:actual=prior/'source-revisions'/(sha+'.py')
        assert digest(actual)==sha,file
    directory=os.add_dll_directory('C:/mingw32/bin');dll=prior/'original-grounding.dll';assert digest(dll)==oracle['oracle_sha256']
    library=C.CDLL(str(dll));library.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    rom=ROOT/'Lion King, The (USA).sfc';assert digest(rom)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert library.terrain_native_init(rom.read_bytes(),0x300000)
    library.grounding_snapshot_run.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_uint),C.c_void_p,C.POINTER(C.c_uint),C.c_void_p,C.c_void_p]
    result={};sources={}
    for host,cases in (('headless',CASES),('windows',WINDOWS)):
        for case in cases:
            folder=base/('scoped-'+host)/name(case);report=folder/'report.json';r=json.loads(report.read_text());assert r['result']=='PASS'
            sources[str(report.relative_to(ROOT)).replace('\\','/')]=digest(report)
            for n,scene in enumerate(r['scenes']):
                capture=folder if n==0 else folder/scene['folder'];fields=('a','x','y','stack','direct_page','db','p','emulation')
                entry=next(csv.DictReader((capture/'ground-entry.csv').open()));returned=next(csv.DictReader((capture/'ground-return.csv').open()))
                abi=[int(entry[k]) for k in fields];wanted=[int(returned[k]) for k in fields]
                assert int(entry['age'])==int(returned['age'])==268
                before=(capture/'ground-entry.bin').read_bytes();after=(capture/'ground-return.bin').read_bytes()
                output=C.create_string_buffer(0x20000);reads=C.create_string_buffer(0x20000);writes=C.create_string_buffer(0x20000);registers=(C.c_uint*11)()
                assert library.grounding_snapshot_run(before,len(before),(C.c_uint*8)(*abi),output,registers,reads,writes)
                assert output.raw==after and list(registers)[:8]==wanted,(host,case,n)
                assert list(registers)[8:]==[144,0,0xc087fe]
                assert int.from_bytes(after[0xb21d:0xb21f],'little')==1255
                assert int.from_bytes(before[0xb21d:0xb21f],'little')==(1248 if case[0]=='snes' else 1255)
                for file in ('ground-entry.csv','ground-entry.bin','ground-return.csv','ground-return.bin'):
                    relative=str((capture/file).relative_to(folder)).replace('\\','/')
                    assert digest(capture/file)==r['artifacts_sha256'][relative]
                result[f'{host}/{name(case)}/{n+1}']=dict(full_ram_and_registers_exact=True,instructions=144,invalid_bus_accesses=0)
    for p in (Path(__file__),dll,prior/'build-report.json',rom,ROOT/'tools/run_pride_repeat_matrix.py'):
        sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    (base/'ground-cpu-report.json').write_text(json.dumps(dict(result='PASS',cases=result,source_sha256=sources),indent=2)+'\n')
    directory.close();print(len(result),'first/second grounding calls match complete original CPU RAM/registers',flush=True)


if __name__=='__main__':main()
