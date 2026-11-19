"""32-bit: full MD-timing Windows clients against the verified installed reader."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels

capture = ROOT/'build/pride-menu246-md-timing/report.json'
ref = bound(capture)
assert ref['result'] == 'PASS'
component = ROOT/'build/pride-final-menu-layout-component/verification/report.json'
assert bound(component)['result'] == 'PASS'
library = component.parent.parent/'reader.dll'
cmd = ref['commands']['selected']
package = Path(cmd[cmd.index('--final-menu-assets')+1])
raw = package.read_bytes(); blob = C.create_string_buffer(raw)
dll = C.CDLL(str(library))
dll.TlkFinalArtLoad.argtypes = [C.c_void_p, C.c_size_t]
dll.TlkFinalArtLoad.restype = C.c_void_p
dll.TlkFinalArtFree.argtypes = [C.c_void_p]
dll.TlkFinalArtDrawMenuViewport.argtypes = [C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
dll.TlkFinalArtDrawConfirmedMenuViewport.argtypes = [C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
art = dll.TlkFinalArtLoad(blob,len(raw)); assert art
canvas = (C.c_uint32*(320*224))()
out = ROOT/'build/pride-menu247-md-pixels'; out.mkdir()
checks = {}; observations = {}
try:
    for name in ('ready','hold','exit-pose','retained-credit'):
        record = ref['observations'][name]; before = record['before']; after = record['after']
        picture = pixels(capture.parent/'selected'/(name+'.png'))
        matches = []
        # Host display-field bounds, not a claim that a window screenshot is atomic.
        for field in range(before['field']-3,after['field']+4):
            age = field-before['entry']; confirmed = before['confirmed_md']
            if confirmed and field>=confirmed:
                ok = dll.TlkFinalArtDrawConfirmedMenuViewport(art,age,confirmed-before['entry'],before['confirmed_credits'],320,canvas)
            else:
                ok = dll.TlkFinalArtDrawMenuViewport(art,age,before['credits_guest'],0,320,canvas)
            assert ok
            image = []
            for y in range(224):
                line = []
                for x in range(320):
                    value = canvas[y*320+x]
                    rgb = tuple((((value>>shift&255)>>3)<<3)|(((value>>shift&255)>>3)>>2) for shift in (16,8,0))
                    line.extend([rgb]*2)
                image.extend(line);image.extend(line)
            if picture == (640,448,image): matches.append(field)
        observations[name] = matches
        checks[name+'_whole_OS_client_exact'] = bool(matches)
        print(name, matches[:5], flush=True)
    checks['observed_confirm_uses_host_clock'] = all(r['before']['age']==r['before']['field']-r['before']['entry'] for r in ref['observations'].values())
    checks['count_retained_after_guest_consumption'] = ref['observations']['retained-credit']['before']['credits_guest']==0 and bool(observations['retained-credit'])
finally:
    dll.TlkFinalArtFree(art)
paths = [Path(__file__),capture,component,library,package]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
    scope='Four complete actual 320 Windows menu clients, unmasked, compared with original-verified installed MD reader using host display-field bounds and actual host confirmation/entry clocks. No original MD CPU-clock equivalence claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL', checks, flush=True)
