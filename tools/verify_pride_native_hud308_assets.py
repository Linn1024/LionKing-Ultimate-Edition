"""Python32: prepared meter glyphs and representative unchanged widget builders."""
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-native-hud307-installed/build-report.json';bound(build)
out=ROOT/'build/pride-native-hud308-assets';out.mkdir();checks={}
sources={'old':ROOT/'build/pride-native-hud305-baseline/engine/runner/tlk_native_hud.c','reader':ROOT/'engine/runner/tlk_native_hud.c'}
for name,src in sources.items():
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(src),str(ROOT/'engine/snesrecomp/runner/src/sha256.c'),'-o',str(out/(name+'.dll'))],check=True)
old=C.CDLL(str(out/'old.dll'));reader=C.CDLL(str(out/'reader.dll'))
old.TlkNativeHudCreate.argtypes=[C.c_void_p,C.c_size_t];old.TlkNativeHudCreate.restype=C.c_void_p
reader.TlkNativeHudLoad.argtypes=[C.c_void_p,C.c_size_t];reader.TlkNativeHudLoad.restype=C.c_void_p
reader.TlkNativeHudClone.argtypes=[C.c_void_p];reader.TlkNativeHudClone.restype=C.c_void_p
for dll in (old,reader):
    dll.TlkNativeHudFree.argtypes=[C.c_void_p]
    dll.TlkNativeHudRestored.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_void_p,C.c_void_p]
    dll.TlkNativeHudRoarCurrent.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint16,C.c_void_p,C.c_void_p]
rom=(ROOT/'Lion King, The (USA).sfc').read_bytes();rb=C.create_string_buffer(rom)
a=old.TlkNativeHudCreate(rb,len(rom));assert a
package=build.parent/'native-hud.assets';raw=package.read_bytes();buffer=C.create_string_buffer(raw);parent=reader.TlkNativeHudLoad(buffer,len(raw));assert parent
b=reader.TlkNativeHudClone(parent);assert b;reader.TlkNativeHudFree(parent);C.memset(buffer,0,len(raw));C.memset(rb,0,len(rom))
checks['exact_original_glyph_bytes']=raw[112:]==rom[0x405ff:0x405ff+0x620]
original=sources['old'].read_text().split('static void block',1)[1].strip()
current=sources['reader'].read_text().split('static void block',1)[1].split('#include "tlk_native_hud_assets.inc"')[0].strip()
checks['meter_builder_sources_unchanged']=original==current
count=0;same=True
try:
    for previous in (bytes(512),bytes([0xa5])*512):
        p=C.create_string_buffer(previous)
        for kind,maximum in ((1,4),(1,6),(1,12),(0,8),(0,16),(0,64)):
            x=C.create_string_buffer(512);y=C.create_string_buffer(512)
            ra=old.TlkNativeHudRestored(a,kind,maximum,p,x);rb=reader.TlkNativeHudRestored(b,kind,maximum,p,y)
            same &= ra==rb==1 and x.raw==y.raw;count+=1
        for maximum in (8,16,64):
            for value in sorted({0,1,4,7,maximum-1,maximum}):
                for initial in (0,1,65535):
                    x=C.create_string_buffer(512);y=C.create_string_buffer(512)
                    ra=old.TlkNativeHudRoarCurrent(a,maximum,value,initial,p,x);rb=reader.TlkNativeHudRoarCurrent(b,maximum,value,initial,p,y)
                    same &= ra==rb==1 and x.raw==y.raw;count+=1
    checks['restored_and_empty_partial_full_roar_owned_clone_exact']=same
finally:old.TlkNativeHudFree(a);reader.TlkNativeHudFree(b)
variants={'truncated':raw[:-1],'checksum':raw[:-1]+bytes([raw[-1]^1])}
for name,offset,value in (('version',8,2),('size',16,0xffffffff),('font_bytes',20,0),('source',24,0),('reserved',88,1)):
    data=bytearray(raw);struct.pack_into('<I',data,offset,value);variants[name]=bytes(data)
for name,data in variants.items():
    p=C.create_string_buffer(data);candidate=reader.TlkNativeHudLoad(p,len(data));checks[name+'_rejects']=not candidate
    if candidate:reader.TlkNativeHudFree(candidate)
symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(out/'reader.dll')],text=True)
checks['runtime_reader_omits_ROM_constructor_and_preparer']='_TlkNativeHudCreate' not in symbols and '_TlkNativeHudPrepare' not in symbols
paths=[Path(__file__),build,package,*sources.values(),ROOT/'engine/runner/tlk_native_hud_assets.inc']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,widget_comparisons=count,
    scope='Exact original font bytes, unchanged meter algorithms, representative restored/empty/partial/full output versus pre-migration constructor after parent/source erasure; malformed records and no runtime constructor.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',count,checks,flush=True)
