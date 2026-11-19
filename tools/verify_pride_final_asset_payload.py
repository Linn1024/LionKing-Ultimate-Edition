"""Compare ROM-decoder output with original Game Over preparation bytes."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-asset-payload';out.mkdir()
    reference=ROOT/'build/pride-final-preparation-probe/capture/report.json';assert bound(reference)['result']=='OBSERVED'
    source=ROOT/'engine/runner/tlk_md_assets.c';sha=ROOT/'engine/snesrecomp/runner/src/sha256.c'
    library=out/'decode.dll';command=['C:/mingw32/bin/gcc.exe','-shared','-O2','-static-libgcc','-Wl,--export-all-symbols',
        '-I'+str(source.parent),'-I'+str(sha.parent),str(source),str(sha),'-o',str(library)]
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    dll=C.CDLL(str(library));dll.TlkMdDecompress.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_void_p,C.c_uint,C.c_void_p]
    rom_path=ROOT/'Lion King, The (USA).sfc';rom=rom_path.read_bytes();data=C.create_string_buffer(rom)
    checks={};rows=[]
    for number,address,destination,size in [(1,0x1545ec,0x10000,35712),(2,0x2f7073,0x7ae4,1536)]:
        buffer=C.create_string_buffer(65536);written=C.c_uint()
        checks[f'{number}/decoded']=bool(dll.TlkMdDecompress(data,len(rom),address,buffer,len(buffer),C.byref(written)))
        original=ROOT/f'build/pride-final-preparation-probe/capture/final/decode-{number:03d}-exit.bin'
        checks[f'{number}/length']=written.value==size
        checks[f'{number}/original_payload']=buffer.raw[:size]==original.read_bytes()[destination:destination+size]
        rows.append(dict(source=address,destination=destination,bytes=size,original_snapshot=original.relative_to(ROOT).as_posix()))
    paths=[Path(__file__),reference,source,source.with_name('tlk_md_assets_cache.inc'),sha,rom_path]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,payloads=rows,command=command,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'both original final-scene asset payloads',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
