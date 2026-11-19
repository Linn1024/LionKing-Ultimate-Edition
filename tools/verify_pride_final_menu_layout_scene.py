"""Check menu edge anchoring against the original-verified320 compositor."""
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def edge_layout(raw,width):
    """Independent pixel transport of the isolated original HUD rectangle."""
    if width==320:return raw
    result=bytearray(raw);black=b'\x00\x00\x00\xff'*64
    for y in range(176,224):
        offset=(y*320+224)*4;hud=raw[offset:offset+64*4]
        result[offset:offset+64*4]=black
        at=(y*320+192)*4;result[at:at+64*4]=hud
    return bytes(result)


def main():
    base=ROOT/'build/pride-final-menu-layout-component';out=base/'verification';out.mkdir();checks={}
    source=ROOT/'build/pride-final-menu-yes-component/verification/report.json';bound(source)
    evidence=ROOT/'build/pride-final-menu-layout-evidence/report.json';bound(evidence)
    previous=ROOT/'build/pride-final-menu-yes-component/reader2.dll';library=base/'reader.dll'
    old=C.CDLL(str(previous));new=C.CDLL(str(library))
    package=ROOT/'build/pride-final-menu-scene/menu.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw)
    for dll in (old,new):
        dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
        dll.TlkFinalArtFree.argtypes=[C.c_void_p]
        dll.TlkFinalArtDrawMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
        dll.TlkFinalArtDrawConfirmedMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.POINTER(C.c_uint32)]
    new.TlkFinalArtDrawMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
    new.TlkFinalArtDrawConfirmedMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
    a=old.TlkFinalArtLoad(blob,len(raw));b=new.TlkFinalArtLoad(blob,len(raw));assert a and b
    x=(C.c_uint32*(320*224))();y=(C.c_uint32*(320*224))()
    try:
        for confirm,start,end in ((124,124,352),(130,124,352),(220,118,448)):
            for age in range(start,end):
                draw_age=min(age,confirm+208)
                if age<confirm:
                    assert old.TlkFinalArtDrawMenu(a,draw_age,3,0,x)
                    assert new.TlkFinalArtDrawMenu(b,draw_age,3,0,y)
                else:
                    assert old.TlkFinalArtDrawConfirmedMenu(a,draw_age,confirm,3,x)
                    assert new.TlkFinalArtDrawConfirmedMenu(b,draw_age,confirm,3,y)
                checks[f'original320_{confirm}_{age}']=bytes(x)==bytes(y)
        for width in (256,320):
            for credit in range(10):
                for age in (118,124,130,132,140,160,220):
                    for selected in (0,1):
                        assert old.TlkFinalArtDrawMenu(a,age,credit,selected,x)
                        assert new.TlkFinalArtDrawMenuViewport(b,age,credit,selected,width,y)
                        checks[f'layout{width}_{credit}_{age}_{selected}']=bytes(y)==edge_layout(bytes(x),width)
                        if credit==1 and not selected and age in (118,130,132,140,160,220):
                            png(out/f'{width}-{age}.png',bytes(y),320,224,1280,1)
            for confirm in (124,130,220):
                for offset in (0,58,59,63,67,69,73,208):
                    age=confirm+offset
                    assert old.TlkFinalArtDrawConfirmedMenu(a,age,confirm,1,x)
                    assert new.TlkFinalArtDrawConfirmedMenuViewport(b,age,confirm,1,width,y)
                    checks[f'exit{width}_{confirm}_{age}']=bytes(y)==edge_layout(bytes(x),width)
            for selected in (0,1):
                assert old.TlkFinalArtDrawMenu(a,140,1,selected,x)
                png(out/f'{width}-no-source{selected}.png',edge_layout(bytes(x),width),320,224,1280,1)
        for width in (0,255,257,319,321,2**32-1):
            before=bytes(y)
            checks[f'invalid_width{width}_rejects']=not new.TlkFinalArtDrawMenuViewport(b,140,1,0,width,y)
            checks[f'invalid_width{width}_preserves_output']=bytes(y)==before
    finally:old.TlkFinalArtFree(a);new.TlkFinalArtFree(b)
    paths=[Path(__file__),source,evidence,previous,package,ROOT/'engine/runner/tlk_final_art.c',ROOT/'engine/runner/tlk_final_art.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,binary_sha256=digest(library),
        scope='Original320 picture parity plus independent credit-HUD pixel transport at256; this is viewport adaptation, not complete SNES menu art/layout',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
