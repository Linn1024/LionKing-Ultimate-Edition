"""Check versioned title intent records and transactional malformed-state rejection."""
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


def main():
    out=ROOT/'build/pride-title-ready-state2';out.mkdir()
    library=out/'state.dll'
    paths=[ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'engine/runner/tlk_continue_scene.c',ROOT/'engine/snesrecomp/runner/src/sha256.c']
    cmd=['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),
         *map(str,paths),'-o',str(library)]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    dll=C.CDLL(str(library))
    dll.TlkFinalSceneStateLoad.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t]
    dll.TlkFinalSceneStateSave.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t]
    files=[ROOT/'build/pride-title-upload16/verification/256-367/saved.state',
           ROOT/'build/pride-final-menu-player8/yes/256-124-182/saved.state']
    def inner(file):
        raw=file.read_bytes();assert raw[:8]==b'TLKFSV01';n,size=struct.unpack_from('<II',raw,20)
        return raw[96+n:96+n+size]
    def seal(raw):
        raw[48:80]=bytes(32);raw[48:80]=hashlib.sha256(raw).digest();return bytes(raw)
    records=[inner(p) for p in files]
    v3=bytearray(records[0]);entry=struct.unpack_from('<I',v3,100)[0]
    struct.pack_into('<I',v3,8,3);struct.pack_into('<II',v3,172,entry+515,0x1000);records.append(seal(v3))
    state=C.create_string_buffer(2*1024*1024);checks={}
    for version,raw in enumerate(records,1):
        source=C.create_string_buffer(raw[16:48]);blob=C.create_string_buffer(raw);output=C.create_string_buffer(len(raw))
        checks[f'v{version}_load']=bool(dll.TlkFinalSceneStateLoad(state,source,blob,len(raw)))
        checks[f'v{version}_save']=bool(dll.TlkFinalSceneStateSave(state,source,output,len(raw)))
        checks[f'v{version}_byte_exact']=output.raw==raw
        checks[f'v{version}_version']=struct.unpack_from('<I',raw,8)[0]==version
    field=struct.unpack_from('<I',records[2],96)[0];flags=struct.unpack_from('<I',records[2],108)[0]
    variants={}
    for label,offset,value in [('unknown-version',8,4),('v3-no-ready',172,0),('past-ready',172,field),
                             ('too-future',172,field+192),('too-early',172,entry+314),('oversized-pad',176,65536),
                             ('no-entry',100,0),('no-target',108,flags&~8),('reserved',180,1),('v1-with-ready',8,1),('v2-with-ready',8,2)]:
        raw=bytearray(records[2]);struct.pack_into('<I',raw,offset,value);variants[label]=seal(raw)
    raw=bytearray(records[0]);struct.pack_into('<I',raw,176,1);variants['orphan-pad']=seal(raw)
    raw=bytearray(records[1]);struct.pack_into('<I',raw,8,3);struct.pack_into('<II',raw,172,field+100,0);variants['confirmed-with-ready']=seal(raw)
    raw=bytearray(records[2]);struct.pack_into('<II',raw,160,entry+323,entry+323);struct.pack_into('<I',raw,108,flags|256)
    raw[192+2*256*224*4:192+3*256*224*4]=bytes(256*224*4)
    variants['inconsistent-fade']=seal(raw)
    raw=bytearray(records[2]);raw[-1]^=1;variants['bad-checksum']=bytes(raw)
    for label,raw in variants.items():
        before=state.raw;source=C.create_string_buffer(raw[16:48]);blob=C.create_string_buffer(raw)
        checks[label+'_rejects']=not dll.TlkFinalSceneStateLoad(state,source,blob,len(raw))
        checks[label+'_preserves_state']=state.raw==before
    paths += [Path(__file__),ROOT/'engine/runner/tlk_final_scene_state.h',*files]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,compile=cmd,binary_sha256=digest(library),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
