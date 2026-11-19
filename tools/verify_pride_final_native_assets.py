"""Compare installer-prepared native payloads to original decoder-exit WRAM."""
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
    _fields_=[(name,C.c_uint32) for name in ('source','destination','source_end','destination_end','size')]


def main():
    base=ROOT/'build/pride-final-native-installed';out=base/'verification';out.mkdir();checks={}
    original=ROOT/'build/pride-final-asset-payload/report.json';bound(original)
    reloads=ROOT/'build/pride-continue-reload-assets/report.json';old=bound(reloads)
    captured=ROOT/'build/pride-continue-reload-probe/capture/report.json';bound(captured)
    library=base/'reader.dll';dll=C.CDLL(str(library))
    dll.TlkFinalNativeLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalNativeLoad.restype=C.c_void_p
    dll.TlkFinalNativeFree.argtypes=[C.c_void_p]
    dll.TlkFinalNativeRecipeAt.argtypes=[C.c_uint];dll.TlkFinalNativeRecipeAt.restype=C.POINTER(Recipe)
    dll.TlkFinalNativePayload.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_size_t)];dll.TlkFinalNativePayload.restype=C.c_void_p
    package=base/'native.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw)
    assets=dll.TlkFinalNativeLoad(blob,len(raw));assert assets;C.memset(blob,0,len(raw))
    checks['owned_after_input_erasure']=True;observations=[]
    try:
        for index in range(10):
            r=dll.TlkFinalNativeRecipeAt(index).contents;size=C.c_size_t()
            pointer=dll.TlkFinalNativePayload(assets,index,C.byref(size));assert pointer
            data=C.string_at(pointer,size.value)
            if index:
                expected=old['recipes'][index-1]
                checks[f'{index}_original_recipe']=all(getattr(r,key)==expected[key] for key,_ in Recipe._fields_)
                snapshot=captured.parent/f'{index}-after.bin'
            else:
                snapshot=ROOT/'build/pride-final-preparation-probe/capture/final/decode-001-exit.bin'
            offset=r.destination&0x1ffff;wram=snapshot.read_bytes()
            checks[f'{index}_size']=size.value==r.size
            checks[f'{index}_original_bytes']=data==wram[offset:offset+r.size]
            observations.append(dict(index=index,source=hex(r.source),destination=hex(r.destination),size=r.size,
                payload_sha256=hashlib.sha256(data).hexdigest(),snapshot=snapshot.relative_to(ROOT).as_posix()))
        size=C.c_size_t(99)
        checks['invalid_index_rejects']=not dll.TlkFinalNativePayload(assets,10,C.byref(size)) and size.value==0
        checks['invalid_recipe_rejects']=not dll.TlkFinalNativeRecipeAt(10)
        variants={}
        for name,offset,value in [('version',8,2),('header-size',12,116),('count',20,9),('reserved',88,1),
            ('source',112,0),('destination',116,0),('source-end',120,1),('destination-end',124,0),('size',128,35711)]:
            data=bytearray(raw);struct.pack_into('<I',data,offset,value);variants[name]=data
        data=bytearray(raw);data[24]^=1;variants['source-identity']=data
        data=bytearray(raw[:-1]);struct.pack_into('<I',data,16,len(data));variants['truncated']=data
        data=bytearray(raw+b'\0');struct.pack_into('<I',data,16,len(data));variants['trailing']=data
        for name,data in variants.items():
            data[56:88]=hashlib.sha256(data[112:]).digest();blob=C.create_string_buffer(bytes(data))
            bad=dll.TlkFinalNativeLoad(blob,len(data));checks[name+'_resealed_rejects']=not bad
            if bad:dll.TlkFinalNativeFree(bad)
        data=bytearray(raw);data[-1]^=1;blob=C.create_string_buffer(bytes(data))
        bad=dll.TlkFinalNativeLoad(blob,len(data));checks['corrupted_payload_rejects']=not bad
        if bad:dll.TlkFinalNativeFree(bad)
    finally:dll.TlkFinalNativeFree(assets)
    helper=base/'cmake/tlk_prepare_final_assets.exe';repeat=out/'repeat.assets'
    result=subprocess.run([str(helper),'--snes-rom',str(ROOT/'Lion King, The (USA).sfc'),'--output',str(repeat)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/'repeat.log').write_bytes(result.stdout);checks['repeat_identical']=result.returncode==0 and repeat.read_bytes()==raw
    result=subprocess.run([str(helper),'--snes-rom',str(ROOT/'Lion King, The (World).md'),'--output',str(repeat)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/'wrong-source.log').write_bytes(result.stdout);checks['wrong_source_rejects_preserves']=result.returncode==4 and repeat.read_bytes()==raw
    checks['md_package_unchanged']=digest(base/'menu.assets')=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(library)],text=True)
    checks['reader_has_no_decoder']='TlkMdDecompress' not in symbols and 'TlkFinalNativePrepare' not in symbols
    paths=[Path(__file__),original,reloads,captured,package,helper,
        *[ROOT/'engine/runner'/n for n in ('tlk_final_native.c','tlk_final_native.h','tlk_final_native_internal.h','tlk_final_native_prepare.c','tlk_final_native_prepare.h')]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,binary_sha256=digest(library),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
