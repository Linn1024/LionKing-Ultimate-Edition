"""Compare package-only menu drawing to sampled original complete pictures."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-menu-scene';out=base/'verification';out.mkdir();checks={}
    source=ROOT/'build/pride-final-menu-art-original/report.json';bound(source)
    library=base/'reader.dll';dll=C.CDLL(str(library))
    dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
    dll.TlkFinalArtFree.argtypes=[C.c_void_p]
    dll.TlkFinalArtDrawMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
    dll.TlkFinalArtAnimation.argtypes=[C.c_void_p,C.c_uint,C.c_uint64,C.POINTER(C.c_uint32)]
    package=base/'menu.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw)
    art=dll.TlkFinalArtLoad(blob,len(raw));assert art;C.memset(blob,0,len(raw))
    core_levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    def host_component(c):
        value=c*4+(c>>2);return value<<3|value>>2
    def expected(path):
        w,h,image=pixels(path)
        return [(host_component(core_levels[0].index(r)),host_component(core_levels[1].index(g)),host_component(core_levels[2].index(b))) for r,g,b in image]
    buffer=(C.c_uint32*(320*224))();different={}
    try:
        for case,credits in [('continue',3),('game-over',0)]:
            for age in (118,120,124,125,140,141,160,180,200,220):
                assert dll.TlkFinalArtDrawMenu(art,age,credits,0,buffer)
                actual=[(v>>16&255,v>>8&255,v&255) for v in buffer]
                gold=expected(source.parent/case/str(age)/'window.png')
                wrong=sum(a!=b for a,b in zip(actual,gold));different[case+str(age)]=wrong
                checks[case+str(age)+'_whole_picture']=wrong==0
                png(out/(case+str(age)+'.png'),bytes(buffer),320,224,1280,1)
        frame=C.c_uint32()
        checks['large_animation_clock']=bool(dll.TlkFinalArtAnimation(art,0,2**64-1,C.byref(frame)))
    finally:dll.TlkFinalArtFree(art)
    # Resealed packages must still pass structural/program referential checks.
    plan=len(raw)-struct.unpack_from('<I',raw,88)[0]
    variants={}
    for name,offset,value in [('unknown-slot',plan,0),('bad-bank',plan+84,4),
        ('bad-loop',plan+108,999),('zero-ticks',plan+116,0)]:
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);data[56:88]=hashlib.sha256(data[112:]).digest();variants[name]=data
    for name,data in variants.items():
        blob=C.create_string_buffer(bytes(data));candidate=dll.TlkFinalArtLoad(blob,len(data));checks[name+'_rejects']=not candidate
        if candidate:dll.TlkFinalArtFree(candidate)
    paths=[Path(__file__),source,package,ROOT/'engine/runner/tlk_final_art.c',ROOT/'engine/runner/tlk_final_art.h',
        ROOT/'engine/runner/tlk_final_art_prepare.c',ROOT/'engine/runner/tlk_final_art_internal.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,differing_pixels=different,
        colour_comparison='Reference RGB565 converted to the established MD RGB555 host response',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},binary_sha256=digest(library),
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values()),different


if __name__=='__main__':main()
