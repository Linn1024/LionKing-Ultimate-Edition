"""Compare the pure navigation sampler with original held/priority recordings."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


class Nav(C.Structure):
    _fields_=[('owner',C.c_uint32),('next_field',C.c_uint32),('previous_pad',C.c_uint32)]


def main():
    out=ROOT/'build/pride-title-navigation-model2';out.mkdir()
    source=ROOT/'build/pride-title-navigation-edges2/report.json';original=bound(source)
    library=out/'navigation.dll';c=ROOT/'engine/runner/tlk_title_navigation.c'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared',str(c),'-o',str(library)]
    subprocess.run(cmd,check=True);dll=C.CDLL(str(library))
    dll.TlkTitleNavigationInput.argtypes=[C.POINTER(Nav),C.c_uint32,C.c_uint16,C.c_uint16,C.c_uint16,C.c_uint]
    dll.TlkTitleNavigationInput.restype=C.c_uint16
    dll.TlkTitleNavigationValid.argtypes=[C.POINTER(Nav),C.c_uint32]
    checks={};observations={}
    mapping={8:0x1000,16:0x800,32:0x400}
    for label,row in original['observations'].items():
        nav=Nav();selection=0;prior=0;confirmed=None;events=[]
        for field in range(515,651):
            md=row['events'].get(str(field),0);held=sum(bit for mask,bit in mapping.items() if md&mask)
            native=held&~(prior&0xf0c0);prior=held
            value=dll.TlkTitleNavigationInput(C.byref(nav),field,0xb213,held,native,selection)
            if value&0xc00:selection=0 if value&0x800 else 1;events.append([field,'navigation',selection])
            elif value&0xd0c0:
                confirmed=(field,selection);events.append([field,'confirm',selection]);break
        result=('open' if confirmed[1] else 'start'+str(confirmed[0])) if confirmed else ('selected' if selection else 'idle')
        checks[label+'_original_outcome']=result==row['outcome'];observations[label]=dict(outcome=result,events=events)
    # Capture/reconstruct the actual unobserved-release interval at523.
    nav=Nav();dll.TlkTitleNavigationInput(C.byref(nav),515,0xb213,0x400,0x400,0)
    frozen=bytes(nav);restored=Nav.from_buffer_copy(frozen)
    checks['cold523_valid']=bool(dll.TlkTitleNavigationValid(C.byref(restored),523))
    checks['same_direction524_suppressed']=dll.TlkTitleNavigationInput(C.byref(restored),524,0xb213,0x400,0x400,1)==0
    dll.TlkTitleNavigationInput(C.byref(nav),524,0xb213,0,0,1)
    checks['released_then_same525_wraps']=dll.TlkTitleNavigationInput(C.byref(nav),525,0xb213,0x400,0x400,1)==0x800
    nav=Nav();checks['native_suppressed_first_start_preserved']=dll.TlkTitleNavigationInput(C.byref(nav),515,0xb213,0x1000,0,0)==0
    paths=[Path(__file__),source,c,ROOT/'engine/runner/tlk_title_navigation.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,compile=cmd,
                binary_sha256=digest(library),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
