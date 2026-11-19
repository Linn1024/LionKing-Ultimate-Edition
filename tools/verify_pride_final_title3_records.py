"""Validate real final-scene records and atomic rejection of damaged metadata."""
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


def main():
    out=ROOT/'build/pride-final-title-record-checks';out.mkdir()
    reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';assert bound(reference)['result']=='PASS'
    source=ROOT/'engine/runner/tlk_final_scene_state.c';scene=ROOT/'engine/runner/tlk_continue_scene.c'
    sha=ROOT/'engine/snesrecomp/runner/src/sha256.c';abi=out/'abi.c'
    abi.write_text('#include "tlk_final_scene_state.h"\nsize_t FinalSceneAbiSize(void) {return sizeof(TlkFinalSceneState);}\n')
    library=out/'record.dll';cmd=['C:/mingw32/bin/gcc.exe','-shared','-O2','-static-libgcc','-Wl,--export-all-symbols',
        '-I'+str(source.parent),'-I'+str(sha.parent),str(source),str(scene),str(sha),str(abi),'-o',str(library)]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    dll=C.CDLL(str(library));dll.FinalSceneAbiSize.restype=C.c_uint
    dll.TlkFinalSceneStateLoad.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint]
    dll.TlkFinalSceneStateSave.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint]
    count=dll.FinalSceneAbiSize();checks={};samples={}
    for age in (100,180,300,407,420,433):
        saved=ROOT/'build/pride-final-title3/verification/save180/saved.state' if age==180 else reference.parent/str(age)/'saved.state'
        data=saved.read_bytes();n,p=struct.unpack_from('<II',data,20)
        raw=data[96+n:96+n+p];samples[age]=raw;key=C.create_string_buffer(raw[16:48])
        state=C.create_string_buffer(count);record=C.create_string_buffer(raw);encoded=C.create_string_buffer(len(raw))
        checks[f'{age}/read']=dll.TlkFinalSceneStateLoad(state,key,record,len(raw))==1
        checks[f'{age}/canonical_roundtrip']=dll.TlkFinalSceneStateSave(state,key,encoded,len(raw))==1 and encoded.raw==raw
    cases=[]
    def altered(name,age,offset,value,width=4):
        b=bytearray(samples[age]);b[offset:offset+width]=value.to_bytes(width,'little');b[48:80]=bytes(32)
        b[48:80]=hashlib.sha256(b).digest();cases.append((name,bytes(b),samples[age][16:48]))
    for name,age,offset,value in [
        ('version',100,8,2),('declared_length',100,12,len(samples[100])+4),
        ('reserved_header',100,80,1),('reserved_metadata',100,160,1),('zero_field',100,96,0),
        ('future_entry',100,100,999999),('wrong_age',100,104,99),('unknown_flags',100,108,511),
        ('bad_wait_stack',100,128,0x100),('bad_input_stage',100,144,2),
        ('future_confirmation',300,148,999999),('wrong_origin',300,156,0xc0080d),
        ('early_confirmation',300,148,3994),('unknown_reload_bit',407,112,512),
        ('unused_canvas_data',100,192+2*256*224*4,1)]:altered(name,age,offset,value)
    for name,offset,value in [('title_without_target',108,135),('title_with_reload',112,1),('title_unknown_bit',108,399)]:altered(name,180,offset,value)
    b=bytearray(samples[180]);struct.pack_into('<QI',b,148,4018,0xc00387);b[48:80]=bytes(32);b[48:80]=hashlib.sha256(b).digest();cases.append(('title_with_yes',bytes(b),samples[180][16:48]))
    b=bytearray(samples[100]);b[-1]^=1;cases.append(('damaged_canvas',bytes(b),samples[100][16:48]))
    cases.append(('truncated',samples[100][:-1],samples[100][16:48]))
    cases.append(('trailing_data',samples[100]+b'X',samples[100][16:48]))
    cases.append(('wrong_source',samples[100],bytes([1])*32))
    cases.append(('zero_source',samples[100],bytes(32)))
    for name,raw,key in cases:
        state=C.create_string_buffer(b'Z'*count,count);before=state.raw
        record=C.create_string_buffer(raw);identity=C.create_string_buffer(key)
        checks[name+'/reject']=dll.TlkFinalSceneStateLoad(state,identity,record,len(raw))==0
        checks[name+'/preserve_destination']=state.raw==before
    paths=[Path(__file__),reference,source,source.with_suffix('.h'),scene,sha,abi,ROOT/'build/pride-final-title3/verification/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,runtime_state_bytes=count,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values()),{k:v for k,v in checks.items() if not v}


if __name__=='__main__':main()
