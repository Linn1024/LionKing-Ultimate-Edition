"""Python32: original revival images versus owned prepared data and clones."""
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
build=ROOT/'build/pride-revival297-installed/build-report.json';bound(build)
out=ROOT/'build/pride-revival298-assets';out.mkdir();checks={}
sources={'old':ROOT/'build/pride-revival295-baseline/engine/runner/tlk_revival_art.c','reader':ROOT/'engine/runner/tlk_revival_art.c'}
common=[ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/snesrecomp/runner/src/sha256.c']
for name,src in sources.items():
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(src),*map(str,common),'-o',str(out/(name+'.dll'))],check=True)
old=C.CDLL(str(out/'old.dll'));reader=C.CDLL(str(out/'reader.dll'))
old.TlkRevivalArtCreate.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];old.TlkRevivalArtCreate.restype=C.c_void_p
reader.TlkRevivalArtLoad.argtypes=[C.c_void_p,C.c_size_t];reader.TlkRevivalArtLoad.restype=C.c_void_p
reader.TlkRevivalArtClone.argtypes=[C.c_void_p];reader.TlkRevivalArtClone.restype=C.c_void_p
for dll in (old,reader):
    dll.TlkRevivalArtFree.argtypes=[C.c_void_p]
    dll.TlkRevivalArtCount.argtypes=[C.c_void_p]
    dll.TlkRevivalArtSourceBounds.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,*([C.POINTER(C.c_int)]*4)]
    dll.TlkRevivalArtPixel.argtypes=[C.c_void_p,C.c_uint32,C.c_int,C.c_int,C.c_uint]
snes=(ROOT/'Lion King, The (USA).sfc').read_bytes();md=(ROOT/'Lion King, The (World).md').read_bytes()
sb=C.create_string_buffer(snes);mb=C.create_string_buffer(md);a=old.TlkRevivalArtCreate(sb,len(snes),mb,len(md));assert a
package=build.parent/'revival.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw);parent=reader.TlkRevivalArtLoad(blob,len(raw));assert parent
b=reader.TlkRevivalArtClone(parent);assert b;reader.TlkRevivalArtFree(parent)
C.memset(blob,0,len(raw));C.memset(sb,0,len(snes));C.memset(mb,0,len(md))
checks['original_count_and_owned_clone']=old.TlkRevivalArtCount(a)==reader.TlkRevivalArtCount(b)==13
at=192;poses=[]
for i in range(13):
    pose,x,y,w,h=struct.unpack_from('<IiiII',raw,at);poses.append(pose);at+=20+w*h
assert at==len(raw);count=0
try:
    for i,pose in enumerate(poses):
        same=True
        for source in (0,1):
            ga=[C.c_int() for _ in range(4)];gb=[C.c_int() for _ in range(4)]
            assert old.TlkRevivalArtSourceBounds(a,pose,source,*map(C.byref,ga)) and reader.TlkRevivalArtSourceBounds(b,pose,source,*map(C.byref,gb))
            same &= [v.value for v in ga]==[v.value for v in gb];x,y,w,h=[v.value for v in ga]
            for yy in range(y-1,y+h+1):
                for xx in range(x-1,x+w+1):
                    same &= old.TlkRevivalArtPixel(a,pose,xx,yy,source)==reader.TlkRevivalArtPixel(b,pose,xx,yy,source);count+=1
        checks[f'pose{i}_both_sources_pixels_bounds_owned_after_parent_erased']=same
    checks['unknown_pose_rejected']=reader.TlkRevivalArtPixel(b,0,0,0,0)==-1
finally:old.TlkRevivalArtFree(a);reader.TlkRevivalArtFree(b)
variants={'truncated':raw[:-1],'checksum':raw[:-1]+bytes([raw[-1]^1])}
for name,offset,value in (('version',8,2),('count',20,14),('source',24,0),('reserved',120,1),('pose',192,0),('width',204,0xffffffff),('pixel',212,16)):
    data=bytearray(raw)
    if name=='pixel':data[offset]=value
    else:struct.pack_into('<I',data,offset,value)
    if name in ('pose','width','pixel'):data[88:120]=hashlib.sha256(data[192:]).digest()
    variants[name]=bytes(data)
for name,data in variants.items():
    buffer=C.create_string_buffer(data);candidate=reader.TlkRevivalArtLoad(buffer,len(data));checks[name+'_rejects']=not candidate
    if candidate:reader.TlkRevivalArtFree(candidate)
symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(out/'reader.dll')],text=True)
checks['reader_omits_all_original_image_constructors_and_preparer']=all(name not in symbols for name in ('_TlkRevivalArtCreate','_TlkRevivalArtPrepare'))
paths=[Path(__file__),build,package,*sources.values(),*common,ROOT/'engine/runner/tlk_revival_art_assets.inc']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,original_pixel_samples=count,package_bytes=len(raw),
    scope='All thirteen original revival/idle pairs versus pre-migration decoder, deep clone after parent/source erasure, malformed record rejection, no original image constructors in runtime reader. Animation metadata/hardware remain separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',count,checks,flush=True)
