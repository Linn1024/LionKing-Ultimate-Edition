"""Verify v2 title payloads against original decoder-exit WRAM and v1 bytes."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

class Recipe(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('source','destination','source_end','destination_end','size')]

def main():
    base=ROOT/'build/pride-title-native-installed';out=base/'verification';out.mkdir();checks={}
    original=ROOT/'build/pride-title-native-payloads/report.json';bound(original)
    timing=ROOT/'build/pride-game-over-title-evidence2/report.json';trace=bound(timing)['timings']['320']['decoder_pairs']
    previous=ROOT/'build/pride-final-native-installed/verification/report.json';bound(previous)
    old=(ROOT/'build/pride-final-native-installed/native.assets').read_bytes();pos=112;old_payloads=[]
    for i in range(10):
        recipe=struct.unpack_from('<5I',old,pos);pos+=20;old_payloads.append((recipe,old[pos:pos+recipe[4]]));pos+=recipe[4]
    dll=C.CDLL(str(base/'reader.dll'))
    dll.TlkFinalNativeLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalNativeLoad.restype=C.c_void_p
    dll.TlkFinalNativeFree.argtypes=[C.c_void_p]
    dll.TlkFinalNativeRecipeAt.argtypes=[C.c_uint];dll.TlkFinalNativeRecipeAt.restype=C.POINTER(Recipe)
    dll.TlkFinalNativePayload.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_size_t)];dll.TlkFinalNativePayload.restype=C.c_void_p
    raw=(base/'native.assets').read_bytes();blob=C.create_string_buffer(raw);assets=dll.TlkFinalNativeLoad(blob,len(raw));assert assets
    C.memset(blob,0,len(raw));observed=[]
    try:
        for i in range(20):
            r=dll.TlkFinalNativeRecipeAt(i).contents;n=C.c_size_t();p=dll.TlkFinalNativePayload(assets,i,C.byref(n));assert p
            data=C.string_at(p,n.value);recipe=tuple(getattr(r,k) for k,_ in Recipe._fields_)
            checks[f'{i}_length']=n.value==r.size
            if i<10:
                checks[f'{i}_v1_recipe_unchanged']=recipe==old_payloads[i][0]
                checks[f'{i}_v1_bytes_unchanged']=data==old_payloads[i][1]
            else:
                t=trace[i-10];expected=tuple(int(t[k],16) for k in ('source','destination','source_end','destination_end'))
                checks[f'{i}_original_endpoints']=recipe[:4]==expected
                for width in (256,320):
                    ram=(original.parent/f'{width}/decoder-{i-10}-wram.bin').read_bytes()
                    offset=r.destination&0x1ffff
                    checks[f'{i}_{width}_original_bytes']=len(ram)==0x20000 and data==ram[offset:offset+r.size]
            observed.append(dict(index=i,recipe=recipe,payload_sha256=hashlib.sha256(data).hexdigest()))
        n=C.c_size_t(99)
        checks['index_bounds']=not dll.TlkFinalNativeRecipeAt(20) and not dll.TlkFinalNativePayload(assets,20,C.byref(n)) and n.value==0
    finally:dll.TlkFinalNativeFree(assets)
    def rejected(name,data,reseal=False):
        if reseal:data[56:88]=hashlib.sha256(data[112:]).digest()
        blob=C.create_string_buffer(bytes(data));p=dll.TlkFinalNativeLoad(blob,len(data));checks[name]=not p
        if p:dll.TlkFinalNativeFree(p)
    rejected('old_v1_rejects',old)
    for name,offset,value in [('version',8,1),('count',20,19),('header',12,116),('reserved',88,1),
                               ('title-source',131582,0),('title-destination',131586,0),('title-end',131590,0),('title-length',131598,4813)]:
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);rejected(name,data,True)
    data=bytearray(raw);data[-1]^=1;rejected('payload_corruption',data)
    data=bytearray(raw);data[24]^=1;rejected('source_identity',data)
    for name,data in [('truncated',bytearray(raw[:-1])),('trailing',bytearray(raw+b'\0'))]:
        struct.pack_into('<I',data,16,len(data));rejected(name,data,True)
    helper=base/'cmake/tlk_prepare_final_assets.exe';repeat=out/'repeat.assets'
    result=subprocess.run([str(helper),'--snes-rom',str(ROOT/'Lion King, The (USA).sfc'),'--output',str(repeat)],capture_output=True)
    checks['repeat_identical']=result.returncode==0 and repeat.read_bytes()==raw
    result=subprocess.run([str(helper),'--snes-rom',str(ROOT/'Lion King, The (World).md'),'--output',str(repeat)],capture_output=True)
    checks['wrong_source_preserves']=result.returncode==4 and repeat.read_bytes()==raw
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(base/'reader.dll')],text=True)
    checks['decoder_free_reader']='TlkMdDecompress' not in symbols and 'TlkFinalNativePrepare' not in symbols
    checks['md_package_unchanged']=digest(base/'menu.assets')=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    paths=[Path(__file__),original,timing,previous,base/'reader.dll',base/'native.assets',helper,
           *[ROOT/'engine/runner'/n for n in ('tlk_final_native.c','tlk_final_native.h','tlk_final_native_prepare.c')]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observed,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
