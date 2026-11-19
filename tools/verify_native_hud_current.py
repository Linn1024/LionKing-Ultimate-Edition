"""Verify native current-value roar glyphs against the original 65816 callback.

All maxima8..64, current0..maximum, initial transition flags0/1/3/FFFF. Explicit
guest-value/cache/scratch fixtures; not ordinary gameplay or rendered evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-native-hud-current';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text('{"result":"RUNNING"}\n')
    sources=[Path(__file__),ROOT/'tools/pride_native_hud_oracle.c',ROOT/'engine/runner/tlk_native_hud.c',
             ROOT/'engine/runner/tlk_native_hud.h',ROOT/'Lion King, The (USA).sfc',
             ROOT/'engine/tapes/allbugsF.read.tape']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    with (out/'build.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/cmake.exe','--build','engine/build-win','--target','tlk_native_hud_oracle','-j','4'],
                       cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    binary=ROOT/'engine/build-win/tlk_native_hud_oracle.exe';identity=digest(binary)
    tape=out/'boot-neutral.polled.tape'
    tape.write_bytes(sources[-1].read_bytes()[:800*2]+bytes(40000))
    env=os.environ.copy();env['TLK_NATIVE_HUD_PARTIAL']='1';env['TLK_NATIVE_HUD_ORACLE']=str(out/'original-fonts.bin')
    with (out/'run.log').open('wb') as log:
        subprocess.run([str(binary),'--rom',str(sources[4]),'--lle','--frames','12000',
                        '--input-polled',str(tape)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    raw=(out/'original-fonts.bin').read_bytes();assert raw[:8]==b'SNHUD002'
    assert len(raw)==8+8445*1044
    seen=set();health=set();roar_bytes=0;zeros=partials=full=0
    for offset in range(8,len(raw),1044):
        kind,maximum,current,initial,last=struct.unpack_from('<5I',raw,offset)
        if kind:
            assert kind==1 and 4<=maximum<=12 and current==maximum
            health.add(maximum)
        else:
            key=(maximum,current,initial)
            assert key not in seen and initial in (0,1,3,65535)
            seen.add(key);roar_bytes+=512
            zeros+=current==0;full+=current==maximum;partials+=0<current<maximum
    expected={(maximum,current,initial) for maximum in range(8,65) for current in range(maximum+1)
              for initial in (0,1,3,65535)}
    assert seen==expected and health==set(range(4,13))
    assert 'health9/roar8436 current/transition widget cases exact PASS' in (out/'run.log').read_text()
    assert digest(binary)==identity
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    result=dict(result='PASS',scope=__doc__,original_roar_cases=len(seen),original_health_full_cases=9,
        original_cpu_roar_font_bytes=roar_bytes,empty_cases=zeros,partial_cases=partials,full_cases=full,
        transition_flags=[0,1,3,65535],source_detached=True,alias_safe=True,atomic_rejection=True,
        original_cpu_execution=True,guest_value_fixtures=True,ordinary_gameplay=False,
        renderer_integration=False,actual_windows_captured=False,full_first_level_fidelity_complete=False,
        probe_sha256=identity,source_sha256=identities,
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p!=report_path})
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    print(str(len(seen))+' original CPU roar current/transition cases, '+str(roar_bytes)+' font bytes exact PASS',flush=True)


if __name__=='__main__':main()
