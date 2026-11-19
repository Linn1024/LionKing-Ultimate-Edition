"""32-bit: complete Windows Continue pixels against original-verified MD art."""
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

capture=ROOT/'build/pride-menu217-windows/report.json';ref=bound(capture);assert ref['result']=='PASS'
component=ROOT/'build/pride-final-menu-layout-component/verification/report.json';assert bound(component)['result']=='PASS'
original=ROOT/'build/pride-menu210-continue/report.json';bound(original)
library=ROOT/'build/pride-final-menu-layout-component/reader.dll'
out=ROOT/'build/pride-menu218-pixels';out.mkdir();checks={};observations={}
cmd=ref['commands']['idle'];package=Path(cmd[cmd.index('--final-menu-assets')+1]);raw=package.read_bytes();blob=C.create_string_buffer(raw)
dll=C.CDLL(str(library));dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
dll.TlkFinalArtFree.argtypes=[C.c_void_p]
dll.TlkFinalArtDrawMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
dll.TlkFinalArtDrawConfirmedMenuViewport.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
art=dll.TlkFinalArtLoad(blob,len(raw));assert art
canvas=(C.c_uint32*(320*224))()
try:
    for case,names in [('idle',('idle',)),('yes',('ready','hold','exit-pose','retained-credit')),('no',('selected-no','fade'))]:
        folder=capture.parent/case;rows=list(csv.DictReader((folder/'menu.csv').open()))
        frames={int(r['field']):r for r in rows if r['kind']=='frame'}
        holds=[int(r['field']) for r in rows if r['kind']=='FinalInputHold']
        confirm=next((int(r['field']) for r in rows if r['kind']=='ContinueTransitionConfirm'),None)
        exiting=next((int(r['field']) for r in rows if r['kind']=='ContinueTitleExit'),None)
        cursor={int(r['field']):r for r in csv.DictReader((original.parent/case/'cursor.csv').open()) if r['kind']=='frame'}
        confirm_updates=sum(f<=confirm for f in holds)-1 if confirm else None
        observations[case]={}
        for name in names:
            observed=ref['observations'][case][name];lo=observed['before']['field']-3;hi=observed['after']['field']+3
            picture=pixels(folder/(name+'.png'));matches=[]
            for field in range(lo,hi+1):
                if field not in frames:continue
                brightness=int(frames[field]['brightness']);brightness=0 if brightness&128 else brightness&15
                if not brightness:continue
                if confirm and field>=confirm:
                    age=124+confirm_updates+field-confirm
                    assert dll.TlkFinalArtDrawConfirmedMenuViewport(art,age,124+confirm_updates,1,256,canvas)
                    updates=confirm_updates;selected=0;elapsed=field-confirm
                else:
                    end=min(field,exiting) if exiting else field
                    updates=sum(f<=end for f in holds)-1
                    at=min(field,exiting-1) if exiting else field
                    selected=int(cursor[at]['x'])>=64
                    assert dll.TlkFinalArtDrawMenuViewport(art,124+updates,1,selected,256,canvas)
                    elapsed=None
                image=[]
                for y in range(224):
                    line=[]
                    for x in range(32,288):
                        value=canvas[y*320+x];rgb=[]
                        for shift in (16,8,0):
                            channel=((value>>shift&255)>>3)*brightness//15
                            rgb.append(channel<<3|channel>>2)
                        line.extend([tuple(rgb)]*2)
                    image.extend(line);image.extend(line)
                if picture==(512,448,image):matches.append(dict(field=field,updates=updates,selected_no=bool(selected),brightness=brightness,confirmation_elapsed=elapsed))
            observations[case][name]=matches
            checks[case+'-'+name+'_complete_OS_client_exact']=bool(matches)
            print(case,name,'matches',matches[:3],flush=True)
    checks['no_actual_selector_is_NO']=any(r['selected_no'] for r in observations['no']['selected-no'])
    checks['no_actual_outgoing_dim']=any(0<r['brightness']<15 for r in observations['no']['fade'])
    checks['yes_actual_exit_animation_after_hold']=any(r['confirmation_elapsed']>=59 for r in observations['yes']['exit-pose'])
    checks['yes_count1_after_guest_credit_consumed']=ref['observations']['yes']['retained-credit']['before']['credits']==0 and bool(observations['yes']['retained-credit'])
finally:dll.TlkFinalArtFree(art)
paths=[Path(__file__),capture,component,original,library,package]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
    scope='Complete actual256 Windows idle/YES/NO clients match original-verified installed MD artwork with observed native ownership/loop clocks, MD confirmation art program and native duration/brightness. Capture matching uses explicit display-field ranges; no masks or exact timestamp claim. No public/320/save/source-switch claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
