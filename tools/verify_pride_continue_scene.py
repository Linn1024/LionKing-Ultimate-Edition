"""Check the maintained Continue clock against original palettes and movement."""
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

class Scene(C.Structure):
    _fields_=[('confirmed',C.c_uint64),('origin',C.c_uint32)]
class View(C.Structure):
    _fields_=[('phase',C.c_int),('step',C.c_uint),('controls',C.c_uint)]


def main():
    out=ROOT/'build/pride-continue-scene-model';out.mkdir()
    reference=ROOT/'build/pride-continue-transition-reference/report.json';assert bound(reference)['result']=='OBSERVED'
    control=ROOT/'build/pride-continue-control-reference/report.json';movement=bound(control)
    source=ROOT/'engine/runner/tlk_continue_scene.c';library=out/'clock.dll'
    cmd=['C:/mingw32/bin/gcc.exe','-shared','-O2','-static-libgcc','-Wl,--export-all-symbols',str(source),'-o',str(library)]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    dll=C.CDLL(str(library));dll.TlkContinueSceneBegin.argtypes=[C.POINTER(Scene),C.c_uint32,C.c_uint64]
    dll.TlkContinueSceneView.argtypes=[C.POINTER(Scene),C.c_uint64,C.POINTER(View)]
    for name in ('TlkContinueSceneMdComponent','TlkContinueSceneNativeComponent'):
        getattr(dll,name).argtypes=[C.POINTER(View),C.c_uint];getattr(dll,name).restype=C.c_uint
    checks={};counts={}
    for confirm in (124,130):
        scene=Scene();checks[f'{confirm}/begin']=dll.TlkContinueSceneBegin(C.byref(scene),0xc00387,confirm)==1
        checks[f'{confirm}/duplicate_rejected']=dll.TlkContinueSceneBegin(C.byref(scene),0xc00387,confirm+1)==0
        rows=json.loads((reference.parent/str(confirm)/'timeline.json').read_text())
        palette=lambda age:struct.unpack('<64H',bytes.fromhex(rows[age]['cram']))
        outgoing=palette(confirm+208);incoming=palette(confirm+306);comparisons=0;matches=True
        for age in range(confirm+209,confirm+307):
            v=View();assert dll.TlkContinueSceneView(C.byref(scene),age,C.byref(v))
            actual=palette(age);target=outgoing if v.phase==1 else incoming
            for src,dst in zip(target,actual):
                for shift in (0,3,6):
                    matches &= dll.TlkContinueSceneMdComponent(C.byref(v),(src>>shift)&7)==((dst>>shift)&7)
                    comparisons+=1
        checks[f'{confirm}/all_original_fade_palettes']=matches;counts[str(confirm)]=comparisons
        first=movement['cases'][str(confirm)]['first_movement'];v=View();before=View()
        dll.TlkContinueSceneView(C.byref(scene),first,C.byref(v));dll.TlkContinueSceneView(C.byref(scene),first-1,C.byref(before))
        checks[f'{confirm}/actual_control_boundary']=v.controls==1 and before.controls==0
        checks[f'{confirm}/no_view_before_confirm']=dll.TlkContinueSceneView(C.byref(scene),confirm-1,C.byref(v))==0
    scene=Scene();checks['unsupported_origin_rejected']=dll.TlkContinueSceneBegin(C.byref(scene),0xc0080d,124)==0
    checks['zero_field_rejected']=dll.TlkContinueSceneBegin(C.byref(scene),0xc00387,0)==0
    full=View(4,7,1);black=View(2,7,0)
    checks['all_native_colours_preserved_at_full']=all(dll.TlkContinueSceneNativeComponent(C.byref(full),i)==i for i in range(32))
    checks['all_native_colours_black_at_black']=all(dll.TlkContinueSceneNativeComponent(C.byref(black),i)==0 for i in range(32))
    paths=[Path(__file__),source,source.with_suffix('.h'),reference,control]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,palette_components_compared=counts,
        native_palette_projection_is_hybrid=True,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,counts,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
