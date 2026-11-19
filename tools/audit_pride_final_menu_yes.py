"""Identify every original confirmed-menu picture from installed sprite data."""
import array
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
    out=ROOT/'build/pride-final-menu-yes-audit';out.mkdir()
    source=ROOT/'build/pride-final-menu-yes-original/report.json';data=bound(source)
    videos=ROOT/'build/pride-continue-transition-reference/report.json';video_data=bound(videos)
    library=ROOT/'build/pride-final-menu-yes-component/reader.dll'
    dll=C.CDLL(str(library));dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
    dll.TlkFinalArtFree.argtypes=[C.c_void_p]
    dll.TlkFinalArtDrawMenuClocks.argtypes=[C.c_void_p,C.c_uint,C.c_uint64,C.c_uint64,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
    package=ROOT/'build/pride-final-menu-scene/menu.assets';raw=package.read_bytes()
    blob=C.create_string_buffer(raw);art=dll.TlkFinalArtLoad(blob,len(raw));assert art
    plan=len(raw)-struct.unpack_from('<I',raw,88)[0];pos=plan+104;programs=[]
    for i in range(3):
        n,loop=struct.unpack_from('<II',raw,pos);pos+=8
        steps=[struct.unpack_from('<II',raw,pos+j*8) for j in range(n)];pos+=n*8;programs.append(steps)
    # Compare exact original full pictures in 3-bit RGB space. This avoids the
    # reference core's RGB565 versus the host's RGB555 display quantization.
    r5=[0,4,8,12,17,21,25,29];g6=[0,8,17,25,34,42,51,59]
    lookup={r<<11|g<<5|b:(r5.index(r),g6.index(g),r5.index(b)) for r in r5 for g in g6 for b in r5}
    host={((v<<3)|(v>>2)):i for i,v in enumerate(r5)}
    buffer=(C.c_uint32*(320*224))();pictures=[]
    try:
        for program in (0,1):
            updates=0
            for step,(frame,ticks) in enumerate(programs[program]):
                for icon in range(4):
                    assert dll.TlkFinalArtDrawMenuClocks(art,program,updates,icon*6,3,0,buffer)
                    rgb=bytes(c for v in buffer for c in (host[v>>16&255],host[v>>8&255],host[v&255]))
                    pictures.append((dict(program=program,step=step,frame=hex(frame),icon=icon),rgb))
                updates+=ticks
    finally:dll.TlkFinalArtFree(art)
    cache={};checks={};observations={}
    for case,rows in data['cases'].items():
        confirm=int(case);frames={r['age']:r for r in video_data['cases'][case]['video_frames']};result=[]
        with (videos.parent/case/'video.bin').open('rb') as video:
            for row in rows:
                age=row['age']
                if age<124:continue
                step=max(0,min(7,(age-confirm-206)//3)) if age>=confirm+209 else 0
                if step not in cache:
                    cache[step]={}
                    for identity,rgb in pictures:
                        faded=bytes(max(0,v-step) for v in rgb)
                        cache[step].setdefault(hashlib.sha256(faded).hexdigest(),[]).append(identity)
                f=frames[age];video.seek(f['offset']);raw=video.read(f['bytes']);rgb=bytearray()
                for y in range(224):
                    words=array.array('H',raw[y*f['pitch']:y*f['pitch']+640])
                    for v in words:rgb.extend(lookup[v])
                matches=cache[step].get(hashlib.sha256(rgb).hexdigest(),[])
                checks[case+'_'+str(age)+'_whole_picture']=bool(matches)
                result.append(dict(age=age,fade_step=step,matches=matches))
        observations[case]=result
    paths=[Path(__file__),source,videos,package,ROOT/'engine/runner/tlk_final_art.c',ROOT/'engine/runner/tlk_final_art.h']
    report=dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,observations=observations,
        scope='Exact complete original pictures after matching RGB3 values; identifies pictures, not scene clock implementation',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},binary_sha256=digest(library))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
