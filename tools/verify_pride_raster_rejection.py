"""Reject an invalid native raster cursor through real F5 while owned."""
from pathlib import Path
from audit_scenes import ROOT


if __name__=='__main__':
    source=(ROOT/'tools/verify_pride_practice_rejection.py').read_text()
    old_damage="""    if md:raw[56]^=1
    else:
        raw[256+36]^=1
        raw[56:88]=bytes(32)
        import hashlib
        raw[56:88]=hashlib.sha256(raw).digest()"""
    damage="""    blob_start=256+36
    blob_end=blob_start+struct.unpack_from('<Q',raw,256+24)[0]
    raster=raw.rfind(b'PPRJ',blob_start,blob_end)
    assert raster>=blob_start and raster+65536<=blob_end
    assert struct.unpack_from('<I',raw,raster+4)[0]==1
    struct.pack_into('<I',raw,raster+8,2) # cur must be0 or1
    raw[56:88]=bytes(32)
    import hashlib
    raw[56:88]=hashlib.sha256(raw).digest()"""
    replacements={
        "base=ROOT/'build/pride-practice'":"base=ROOT/'build/pride-raster-state'",
        "binary=base/'practice-sdl.exe'":"binary=base/'live/runtime/practice-live.exe'",
        "author=base/'verified/normal-ui'/name":"author=base/'live'/('md-media' if md else 'native')",
        "state=author/'automatic-original.state'":"state=author/'baseline/tlk_practice_restart.state'",
        old_damage:damage,
        "error='Ordinary-play save is incompatible or damaged' if md else 'State audio continuation is incompatible or damaged'":"error='State audio continuation is incompatible or damaged'",
        "expected=toast_image(control/'window.png',control/'guest.png','Slot 1: '+error)":"from verify_pride_overlay import mixed_toast\n    expected=mixed_toast(control/'window.png','Slot 1: '+error)",
        "paths=(Path(__file__),build_path":"paths=(Path(__file__),ROOT/'tools/verify_pride_practice_rejection.py',ROOT/'tools/verify_pride_overlay.py',build_path",
    }
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
