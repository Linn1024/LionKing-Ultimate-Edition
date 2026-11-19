"""Verify confirmed artwork counters persist and malformed records reject atomically."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-final-menu-yes-component';out=base/'state-verification2';out.mkdir()
    library=base/'state.dll';dll=C.CDLL(str(library))
    dll.TlkFinalSceneStateLoad.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t]
    dll.TlkFinalSceneStateSave.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t]
    old=ROOT/'build/pride-final-menu-player5/continue/report.json';bound(old)
    new=ROOT/'build/pride-final-menu-player8/yes/report.json';bound(new)
    files=[old.parent/'256-140/saved.state',new.parent/'256-124-182/saved.state']
    def inner(file):
        raw=file.read_bytes();assert raw[:8]==b'TLKFSV01'
        native,private=struct.unpack_from('<II',raw,20)
        return raw[96+native:96+native+private]
    checks={};state=C.create_string_buffer(2*1024*1024)
    records=[inner(file) for file in files]
    for version,raw in enumerate(records,1):
        source=C.create_string_buffer(raw[16:48]);blob=C.create_string_buffer(raw)
        checks[f'v{version}_load']=bool(dll.TlkFinalSceneStateLoad(state,source,blob,len(raw)))
        output=C.create_string_buffer(len(raw))
        checks[f'v{version}_save']=bool(dll.TlkFinalSceneStateSave(state,source,output,len(raw)))
        checks[f'v{version}_byte_exact_roundtrip']=output.raw==raw
        checks[f'v{version}_version']=struct.unpack_from('<I',raw,8)[0]==version
    raw=records[1];checks['captured_credit_count']=struct.unpack_from('<I',raw,168)[0]==1
    variants={}
    for name,offset,value in [('zero-credit',168,0),('ten-credits',168,10),('unknown-version',8,3),('v1-has-credit',8,1)]:
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);variants[name]=data
    data=bytearray(raw);data[148:160]=bytes(12);variants['credits-without-confirmation']=data
    data=bytearray(raw);data[172]=1;variants['nonzero-reserved']=data
    for name,data in variants.items():
        data[48:80]=bytes(32);data[48:80]=hashlib.sha256(data).digest()
        before=state.raw;source=C.create_string_buffer(bytes(data[16:48]));blob=C.create_string_buffer(bytes(data))
        checks[name+'_rejects']=not dll.TlkFinalSceneStateLoad(state,source,blob,len(data))
        checks[name+'_preserves_state']=state.raw==before
    paths=[Path(__file__),old,new,*files,ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'engine/runner/tlk_final_scene_state.h',ROOT/'engine/runner/tlk_continue_scene.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},binary_sha256=digest(library))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
