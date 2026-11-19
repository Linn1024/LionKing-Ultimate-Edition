"""Check full continuous original YES pictures against installed scene clocks."""
import array
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-final-menu-yes-component';out=base/'verification';out.mkdir()
    sources=[ROOT/'build/pride-final-menu-yes-original/report.json',ROOT/'build/pride-final-menu-yes-late-original/report.json']
    video_report=ROOT/'build/pride-continue-transition-reference/report.json';videos=bound(video_report)
    library=base/'reader2.dll';dll=C.CDLL(str(library))
    dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
    dll.TlkFinalArtFree.argtypes=[C.c_void_p]
    dll.TlkFinalArtDrawMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
    dll.TlkFinalArtDrawConfirmedMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.POINTER(C.c_uint32)]
    package=ROOT/'build/pride-final-menu-scene/menu.assets';raw=package.read_bytes();blob=C.create_string_buffer(raw)
    art=dll.TlkFinalArtLoad(blob,len(raw));assert art;C.memset(blob,0,len(raw))
    r5=[0,4,8,12,17,21,25,29];g6=[0,8,17,25,34,42,51,59]
    lookup={r<<11|g<<5|b:r5.index(r)<<16|g6.index(g)<<8|r5.index(b) for r in r5 for g in g6 for b in r5}
    host={((v<<3)|(v>>2)):i for i,v in enumerate(r5)}
    tables={step:bytes(max(0,host.get(v,0)-step) for v in range(256)) for step in range(8)}
    buffer=(C.c_uint32*(320*224))();checks={};failures=[]
    try:
        for source in sources:
            data=bound(source)
            for case,rows in data['cases'].items():
                confirm=int(case)
                prior=case in videos['cases'] and not (source.parent/case/'video.bin').exists()
                frames={r['age']:r for r in videos['cases'][case]['video_frames']} if prior else {}
                path=video_report.parent/case/'video.bin' if prior else source.parent/case/'video.bin'
                with path.open('rb') as video:
                    for row in rows:
                        age=row['age']
                        if age<124 and prior:continue
                        draw_age=min(age,confirm+208)
                        if age<confirm:ok=dll.TlkFinalArtDrawMenu(art,draw_age,3,0,buffer)
                        else:ok=dll.TlkFinalArtDrawConfirmedMenu(art,draw_age,confirm,3,buffer)
                        assert ok
                        step=max(0,min(7,(age-confirm-206)//3)) if age>=confirm+209 else 0
                        actual=bytes(buffer).translate(tables[step])
                        f=frames.get(age);offset=f['offset'] if f else row['video_offset'];pitch=f['pitch'] if f else row['pitch']
                        size=f['bytes'] if f else row['video_bytes'];video.seek(offset);raw=video.read(size)
                        gold=array.array('I')
                        for y in range(224):gold.extend(lookup[v] for v in array.array('H',raw[y*pitch:y*pitch+640]))
                        same=actual==gold.tobytes();checks[case+'_'+str(age)+'_whole_picture']=same
                        if not same:failures.append(dict(confirm=confirm,age=age,fade=step))
                print('Checked continuous menu YES',confirm,flush=True)
        checks['reject_before_confirmation']=not dll.TlkFinalArtDrawConfirmedMenu(art,123,124,3,buffer)
        checks['reject_without_credits']=not dll.TlkFinalArtDrawConfirmedMenu(art,124,124,0,buffer)
    finally:dll.TlkFinalArtFree(art)
    paths=[Path(__file__),*sources,video_report,package,ROOT/'engine/runner/tlk_final_art.c',ROOT/'engine/runner/tlk_final_art.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,failures=failures,
        scope='Every complete original picture from118/124 through outgoing black, three confirmation times; RGB3 normalization',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},binary_sha256=digest(library))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),failures[:20],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
