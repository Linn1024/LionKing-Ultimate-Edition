"""32-bit: corrected resource-driven320 centre/HUD/confirmed menu pixels."""
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
capture=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(capture);assert ref['result']=='PASS'
control=ROOT/'build/pride-menu221-wide/report.json';assert bound(control)['result']=='PASS'
component=ROOT/'build/pride-final-menu-layout-component/verification/report.json';assert bound(component)['result']=='PASS'
library=ROOT/'build/pride-final-menu-layout-component/reader.dll'
out=ROOT/'build/pride-menu228-corrected-pixels';out.mkdir();checks={};observations={}
cmd=ref['command'];package=Path(cmd[cmd.index('--final-menu-assets')+1]);raw=package.read_bytes();blob=C.create_string_buffer(raw)
dll=C.CDLL(str(library));dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
dll.TlkFinalArtFree.argtypes=[C.c_void_p]
dll.TlkFinalArtDrawMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
dll.TlkFinalArtDrawConfirmedMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
art=dll.TlkFinalArtLoad(blob,len(raw));assert art;canvas=(C.c_uint32*(320*224))()
rows=list(csv.DictReader((control.parent/'yes-aot/menu.csv').open()))
frames={int(r['field']):r for r in rows if r['kind']=='frame'}
holds=[int(r['field']) for r in rows if r['kind']=='FinalInputHold']
confirm=next(int(r['field']) for r in rows if r['kind']=='ContinueTransitionConfirm')
confirmed_updates=sum(f<=confirm for f in holds)-1
try:
    for name in ('ready','hold','exit-pose','retained-credit'):
        observed=ref['observations'][name];lo=observed['before']['field']-3;hi=observed['after']['field']+3
        picture=pixels(capture.parent/(name+'.png'));matches=[]
        for field in range(lo,hi+1):
            if field not in frames:continue
            brightness=int(frames[field]['brightness']);brightness=0 if brightness&128 else brightness&15
            if not brightness:continue
            if field>=confirm:
                age=124+confirmed_updates+field-confirm
                assert dll.TlkFinalArtDrawConfirmedMenuViewport(art,age,124+confirmed_updates,1,320,canvas)
            else:
                assert dll.TlkFinalArtDrawMenuViewport(art,124+sum(f<=field for f in holds)-1,1,0,320,canvas)
            image=[]
            for y in range(224):
                line=[]
                for x in range(320):
                    value=canvas[y*320+x];rgb=[]
                    for shift in (16,8,0):
                        channel=((value>>shift&255)>>3)*brightness//15;rgb.append(channel<<3|channel>>2)
                    line.extend([tuple(rgb)]*2)
                image.extend(line);image.extend(line)
            if picture==(640,448,image):matches.append(field)
        observations[name]=matches;checks[name+'_complete_corrected320_OS_client_exact']=bool(matches)
        print(name,'matched',matches[:5],flush=True)
    checks['resource_source_active_without_development_flags']=all(r['before']['art_mode']==1 and r['before']['transition_mode']==0 for r in ref['observations'].values())
    checks['retained_credit_after_actual_consumption']=ref['observations']['retained-credit']['before']['credits_guest']==0 and bool(observations['retained-credit'])
finally:dll.TlkFinalArtFree(art)
paths=[Path(__file__),capture,control,component,library,package]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
    scope='Complete resource-driven actual320 YES menu windows after selected-viewport centre/HUD fix, against original-verified installed reader and observed native clocks. Explicit display-field sampling ranges, no region masks; other source/lifecycle/release gates remain.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
