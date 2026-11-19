"""Python32: prepared captions versus separately compiled pre-migration decoder."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-caption277-installed/build-report.json';bound(build)
out=ROOT/'build/pride-caption278-assets';out.mkdir();checks={}
common=[str(ROOT/'engine/runner/tlk_revival_art.c'),str(ROOT/'engine/runner/tlk_death_scene.c'),str(ROOT/'engine/snesrecomp/runner/src/sha256.c')]
sources={'old':ROOT/'build/pride-caption275-baseline/engine/runner/tlk_title_art.c','reader':ROOT/'engine/runner/tlk_title_art.c'}
for name,src in sources.items():
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(src),*common,'-o',str(out/(name+'.dll'))],check=True)
old=C.CDLL(str(out/'old.dll'));reader=C.CDLL(str(out/'reader.dll'))
old.TlkTitleArtCreate.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];old.TlkTitleArtCreate.restype=C.c_void_p
reader.TlkTitleArtLoad.argtypes=[C.c_void_p,C.c_size_t];reader.TlkTitleArtLoad.restype=C.c_void_p
for dll in (old,reader):
    dll.TlkTitleArtFree.argtypes=[C.c_void_p]
    dll.TlkTitleArtBounds.argtypes=[C.c_void_p,C.c_uint,*([C.POINTER(C.c_int)]*4)]
    dll.TlkTitleArtSample.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_uint,C.c_uint,C.POINTER(C.c_uint16),C.POINTER(C.c_uint16)]
snes=(ROOT/'Lion King, The (USA).sfc').read_bytes();md=(ROOT/'Lion King, The (World).md').read_bytes()
sb=C.create_string_buffer(snes);mb=C.create_string_buffer(md);expected=old.TlkTitleArtCreate(sb,len(snes),mb,len(md));assert expected
package=build.parent/'captions.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw);actual=reader.TlkTitleArtLoad(blob,len(raw));assert actual
cg=(C.c_uint16*256)();palette=struct.unpack_from('<16H',snes,0x7b93)
for i,c in enumerate(palette):cg[128+i]=c
C.memset(sb,0,len(snes));C.memset(mb,0,len(md));C.memset(blob,0,len(raw))
count=0
try:
    for source in (0,1):
        a=[C.c_int() for _ in range(4)];b=[C.c_int() for _ in range(4)]
        assert old.TlkTitleArtBounds(expected,source,*map(C.byref,a)) and reader.TlkTitleArtBounds(actual,source,*map(C.byref,b))
        checks[f'{source}_original_bounds']=[v.value for v in a]==[v.value for v in b]
        x,y,w,h=[v.value for v in a];same=True
        for pal in (0,1):
            for yy in range(y-1,y+h+1):
                for xx in range(x-1,x+w+1):
                    ca=C.c_uint16();cb=C.c_uint16()
                    ra=old.TlkTitleArtSample(expected,xx,yy,source,pal,cg,C.byref(ca));rb=reader.TlkTitleArtSample(actual,xx,yy,source,pal,cg,C.byref(cb))
                    same &= ra==rb and (ra!=1 or ca.value==cb.value);count+=1
        checks[f'{source}_all_original_pixels_both_palettes_owned_after_input_erased']=same
    cg[129]^=1;ca=C.c_uint16()
    checks['native_flash_guard_preserved']=reader.TlkTitleArtSample(actual,0,0,0,0,cg,C.byref(ca))==-1
finally:old.TlkTitleArtFree(expected);reader.TlkTitleArtFree(actual)
variants={'truncated':raw[:-1],'checksum':raw[:-1]+bytes([raw[-1]^1])}
for name,offset,value in (('version',8,2),('count',20,3),('source',24,0),('reserved',120,1),('width',192+64+8,0xffffffff)):
    data=bytearray(raw);struct.pack_into('<I',data,offset,value)
    if name=='width':data[88:120]=hashlib.sha256(data[192:]).digest()
    variants[name]=bytes(data)
for name,data in variants.items():
    buffer=C.create_string_buffer(data);candidate=reader.TlkTitleArtLoad(buffer,len(data));checks[name+'_rejects']=not candidate
    if candidate:reader.TlkTitleArtFree(candidate)
symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(out/'reader.dll')],text=True)
checks['reader_has_no_title_ROM_constructor_or_preparer']='_TlkTitleArtCreate' not in symbols and '_TlkTitleArtPrepare' not in symbols
paths=[Path(__file__),build,package,*sources.values(),*[Path(p) for p in common],ROOT/'engine/runner/tlk_title_art_assets.inc']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,original_pixel_samples=count,package_bytes=len(raw),
    scope='Prepared caption ownership/bounds/pixels/palettes against pre-migration original decoder, preserved flash guard, malformed record rejection. Caption constructor/preparer absent from reader; unrelated revival/checkpoint decoders remain elsewhere in runtime.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',count,checks,flush=True)
