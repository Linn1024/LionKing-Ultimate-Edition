"""Check unlinked native adapter against complete original camera helpers at natural inputs."""
import ctypes as C
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-hyena-entrance132';out.mkdir()
reference=ROOT/'build/pride-hyena-camera116/report.json';r=bound(reference);assert r['result']=='NATURAL_CAMERA_WINDOW_DIFFERENCE_VERIFIED'
abi=ROOT/'build/pride-hyena-entrance128/report.json';assert bound(abi)['result']=='ORIGINAL_ENTRANCE_ABI_OBSERVED'
source=ROOT/'tools/pride_hyena_entrance_adapter132.c';module=ROOT/'engine/runner/tlk_hyena_entrance.c';test=ROOT/'engine/tests/hyena_entrance_test.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
includes=['-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),'-I'+str(ROOT/'engine/snesrecomp/runner/src/snes')]
component=['C:/mingw32/bin/gcc.exe','-O2',*includes,str(test),str(module),'-o',str(out/'test.exe')];subprocess.run(component,check=True)
result=subprocess.run([str(out/'test.exe')],capture_output=True,text=True);assert result.returncode==0 and result.stdout.strip()=='PASS 3258 checks'
command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',*includes,str(source),str(module),str(runtime),'-o',str(out/'oracle.dll')];subprocess.run(command,check=True)
snespath=ROOT/'Lion King, The (USA).sfc';snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint];assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
native.entrance_native132.argtypes=[C.c_uint]*4+[C.POINTER(C.c_uint)]
frames_path=ROOT/'build/pride-hyena-camera115/frames.json';frames={r['field']:r for r in json.loads(frames_path.read_text())}
cases_path=reference.parent/'cases.json';expected=json.loads(cases_path.read_text());actual=[];hits=0
for row in expected:
    frame=frames[row['field']];values=[]
    for selected in (0,1):
        native.entrance_source132(selected);raw=(C.c_uint*1)();assert native.entrance_native132(frame['x'],frame['y'],frame['camera_x'],frame['camera_y'],raw)
        values.append(raw[0]);hits+=native.entrance_hits132()
    actual.append(dict(field=row['field'],snes=values[0],md=values[1],native_preserved=values[0]==row['snes'],md_matched=values[1]==row['md']))
(out/'cases.json').write_text(json.dumps(actual,indent=2)+'\n')
checks=dict(component_guards_and_source_policy3258=True,all251_natural_camera_inputs=len(actual)==251,
    native_complete_helper_outputs_unchanged=all(r['native_preserved'] for r in actual),selected_complete_helper_outputs_match_original_md=all(r['md_matched'] for r in actual),
    all16_original_camera_differences_reproduced=sum(r['snes']!=r['md'] for r in actual)==16,actual_adapter_seam_executed=hits>0)
paths=[Path(__file__),reference,abi,frames_path,cases_path,source,module,test,ROOT/'engine/runner/tlk_hyena_entrance.h',ROOT/'engine/runner/tlk_hyena_entrance_policy.h',ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,fixtures=len(actual),selected_seam_hits=hits,component_output=result.stdout,commands=dict(component=component,oracle=command),
    capability_or_resource_node_enabled=False,player_binary_changed=False,
    scope='Maintained but unlinked native adapter executes at original C03BDB during complete original helper calls with observed caller/frame ABI. Natural recorded coordinates and bound original MD outputs. No player, menu, native75, audio-wait or full countdown behavior claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Entrance adapter',checks,'selected seam hits',hits,flush=True)
