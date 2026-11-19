"""Compare adapted original native attack with retained original MD executions."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-component';out.mkdir()
    oracle=ROOT/'tools/pride_porcupine_adapter_oracle.c'
    model=ROOT/'engine/runner/tlk_porcupine_attack.c'
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    headers=ROOT/'engine/snesrecomp/runner/src/snes'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(headers),
             '-I'+str(model.parent),str(oracle),str(model),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,cwd=ROOT,check=True)
    source=ROOT/'build/pride-porcupine-attack2/report.json';old=bound(source)
    lib=C.CDLL(str(out/'oracle.dll'));lib.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    assert lib.terrain_native_init(C.create_string_buffer(snes),len(snes))
    lib.porcupine_native_run.argtypes=[C.c_uint]*7+[C.POINTER(C.c_uint)]
    checks={};cases=[]
    for row in old['cases']:
        if row['source']!='md':continue
        raw=(C.c_uint*20)();assert lib.porcupine_native_run(*row['inputs'],raw)
        observed=list(raw);expected=row['observed'][:18]
        checks[str(len(cases))]=observed[:18]==expected
        cases.append(dict(inputs=row['inputs'],observed=observed,original_md=expected))
    paths=[Path(__file__),oracle,model,model.with_suffix('.h'),runtime,headers/'interp816.h',source,
           ROOT/'tools/pride_porcupine_attack_oracle.c',ROOT/'tools/pride_terrain_native_oracle.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                compile_command=command,synthetic_original_cpu_actions=True,
                external_services_intercepted=True,runtime_guards_or_actual_player_proven=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    print('failures',[r for r in cases if r['observed'][:18]!=r['original_md']][:2],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
