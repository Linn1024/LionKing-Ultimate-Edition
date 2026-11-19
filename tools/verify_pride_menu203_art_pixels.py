"""32-bit: qualify native-timing bridge against original-verified menu reader."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels

capture = ROOT/'build/pride-menu202-art-windows/report.json'
ref = bound(capture)
assert ref['result']=='PASS'
component = ROOT/'build/pride-final-menu-layout-component/verification/report.json'
assert bound(component)['result']=='PASS'
library = ROOT/'build/pride-final-menu-layout-component/reader.dll'
out = ROOT/'build/pride-menu203-art-pixels'
out.mkdir()
cmd = ref['command']
package = Path(cmd[cmd.index('--final-menu-assets')+1])
raw = package.read_bytes()
blob = C.create_string_buffer(raw)
dll = C.CDLL(str(library))
dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t]
dll.TlkFinalArtLoad.restype=C.c_void_p
dll.TlkFinalArtFree.argtypes=[C.c_void_p]
dll.TlkFinalArtDrawMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
art=dll.TlkFinalArtLoad(blob,len(raw));assert art
canvas=(C.c_uint32*(320*224))()
rows=list(csv.DictReader((capture.parent/'menu.csv').open()))
frames={int(r['field']):r for r in rows if r['kind']=='frame'}
holds=[int(r['field']) for r in rows if r['kind']=='FinalInputHold']
checks={}
observations={}
try:
    for name in ('idle','fade'):
        observation=ref['observations'][name]
        lo=observation['before']['field']-3
        hi=observation['after']['field']+3
        picture=pixels(capture.parent/(name+'.png'))
        matches=[]
        for field in range(lo,hi+1):
            if field not in frames:continue
            updates=sum(f<=field for f in holds)-1
            assert updates>=0
            brightness=int(frames[field]['brightness'])
            brightness=0 if brightness&128 else brightness&15
            assert dll.TlkFinalArtDrawMenuViewport(art,124+updates,0,0,256,canvas)
            image=[]
            for y in range(224):
                line=[]
                for x in range(32,288):
                    value=canvas[y*320+x]
                    rgb=[]
                    for shift in (16,8,0):
                        channel=((value>>shift&255)>>3)*brightness//15
                        rgb.append(channel<<3|channel>>2)
                    line.extend([tuple(rgb)]*2)
                image.extend(line);image.extend(line)
            if picture==(512,448,image):matches.append(dict(field=field,updates=updates,brightness=brightness))
        observations[name]=matches
        checks[name+'_complete_OS_client_matches_verified_art_and_native_clock']=bool(matches)
    checks['native_fade_is_dim']=any(0<r['brightness']<15 for r in observations['fade'])
    checks['native_idle_is_full_brightness']=any(r['brightness']==15 for r in observations['idle'])
finally:dll.TlkFinalArtFree(art)
paths=[Path(__file__),capture,component,library,package,capture.parent/'menu.csv']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,observations=observations,
    scope='Complete real Windows256 Game Over idle/fade clients match original-verified installed MD artwork '
          'with observed native loop updates/brightness. Capture matching uses an explicit bounded display-field '
          'sampling range, not an exact presentation timestamp. No Continue/full menu capability claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,observations,flush=True)
