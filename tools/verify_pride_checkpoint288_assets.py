"""Python32: prepared checkpoint pixels against the pre-migration decoder."""
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
build=ROOT/'build/pride-checkpoint287-installed/build-report.json';bound(build)
out=ROOT/'build/pride-checkpoint288-assets';out.mkdir();checks={}
common=[ROOT/'engine/runner/tlk_revival_art.c',ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/snesrecomp/runner/src/sha256.c']
sources={'old':ROOT/'build/pride-checkpoint285-baseline/engine/runner/tlk_checkpoint_art.c','reader':ROOT/'engine/runner/tlk_checkpoint_art.c'}
for name,src in sources.items():
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(src),*map(str,common),'-o',str(out/(name+'.dll'))],check=True)
old=C.CDLL(str(out/'old.dll'));reader=C.CDLL(str(out/'reader.dll'))
old.TlkCheckpointArtCreate.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];old.TlkCheckpointArtCreate.restype=C.c_void_p
reader.TlkCheckpointArtLoad.argtypes=[C.c_void_p,C.c_size_t];reader.TlkCheckpointArtLoad.restype=C.c_void_p
for dll in (old,reader):
    dll.TlkCheckpointArtFree.argtypes=[C.c_void_p]
    dll.TlkCheckpointArtPoseBounds.argtypes=[C.c_void_p,C.c_uint32,*([C.POINTER(C.c_int)]*4)]
    dll.TlkCheckpointArtPoseSample.argtypes=[C.c_void_p,C.c_uint32,C.c_int,C.c_int,C.c_uint,C.c_uint,C.POINTER(C.c_uint16),C.POINTER(C.c_uint16)]
snes=(ROOT/'Lion King, The (USA).sfc').read_bytes();md=(ROOT/'Lion King, The (World).md').read_bytes()
sb=C.create_string_buffer(snes);mb=C.create_string_buffer(md);a=old.TlkCheckpointArtCreate(sb,len(snes),mb,len(md));assert a
package=build.parent/'checkpoints.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw);b=reader.TlkCheckpointArtLoad(blob,len(raw));assert b
cg=(C.c_uint16*256)()
for i,c in enumerate(struct.unpack_from('<16H',snes,0x7b93)):cg[128+i]=c
C.memset(sb,0,len(snes));C.memset(mb,0,len(md));C.memset(blob,0,len(raw));count=0
try:
    for pose in (0xc456de,0xc2fde1,0xc2fe18):
        ga=[C.c_int() for _ in range(4)];gb=[C.c_int() for _ in range(4)]
        assert old.TlkCheckpointArtPoseBounds(a,pose,*map(C.byref,ga)) and reader.TlkCheckpointArtPoseBounds(b,pose,*map(C.byref,gb))
        checks[f'{pose:x}_bounds']=[v.value for v in ga]==[v.value for v in gb]
        x,y,w,h=[v.value for v in ga];same=True
        for source in (0,1):
            for pal in (0,1):
                for yy in range(y-1,y+h+1):
                    for xx in range(x-1,x+w+1):
                        ca=C.c_uint16();cb=C.c_uint16();ra=old.TlkCheckpointArtPoseSample(a,pose,xx,yy,source,pal,cg,C.byref(ca));rb=reader.TlkCheckpointArtPoseSample(b,pose,xx,yy,source,pal,cg,C.byref(cb))
                        same &= ra==rb and (ra!=1 or ca.value==cb.value);count+=1
        checks[f'{pose:x}_all_pixels_sources_palettes_owned']=same
    color=C.c_uint16();checks['unknown_pose_rejected']=reader.TlkCheckpointArtPoseSample(b,0,0,0,0,0,cg,C.byref(color))==-1
    cg[129]^=1;checks['native_flash_guard_preserved']=reader.TlkCheckpointArtPoseSample(b,0xc456de,0,0,0,0,cg,C.byref(color))==-1
finally:old.TlkCheckpointArtFree(a);reader.TlkCheckpointArtFree(b)
variants={'truncated':raw[:-1],'checksum':raw[:-1]+bytes([raw[-1]^1])}
for name,offset,value in (('version',8,2),('count',20,4),('source',24,0),('reserved',120,1),('pose',256,0),('width',268,0xffffffff)):
    data=bytearray(raw);struct.pack_into('<I',data,offset,value)
    if name in ('pose','width'):data[88:120]=hashlib.sha256(data[192:]).digest()
    variants[name]=bytes(data)
for name,data in variants.items():
    buffer=C.create_string_buffer(data);candidate=reader.TlkCheckpointArtLoad(buffer,len(data));checks[name+'_rejects']=not candidate
    if candidate:reader.TlkCheckpointArtFree(candidate)
symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(out/'reader.dll')],text=True)
checks['reader_omits_checkpoint_ROM_constructor_and_preparer']='_TlkCheckpointArtCreate' not in symbols and '_TlkCheckpointArtPrepare' not in symbols
paths=[Path(__file__),build,package,*sources.values(),*common,ROOT/'engine/runner/tlk_checkpoint_art_assets.inc']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,original_pixel_samples=count,package_bytes=len(raw),
    scope='All three original checkpoint poses, both artwork/palette sources, original decoder equivalence and owned prepared bytes; unknown pose/flash/data guards. Checkpoint decoder/preparer omitted from reader; unrelated revival startup still exists.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',count,checks,flush=True)
