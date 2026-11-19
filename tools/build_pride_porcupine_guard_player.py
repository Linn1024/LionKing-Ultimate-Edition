"""Repair the live guest scratch-pool guard; retain failed development36."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-porcupine36';old=bound(prior/'build-report.json')
    out=ROOT/'build/pride-porcupine37';out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    source=ROOT/'engine/runner/tlk_porcupine_attack_runtime.c'
    cmd=old['compiles']['attack-runtime'].copy();obj=out/'attack-runtime.obj'
    for flag,value in [('-c',source),('-o',obj),('-MF',out/'attack-runtime.d'),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    index=next(i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==prior/'attack-runtime.obj')
    inputs[index]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',source]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'attack-runtime':cmd},
                fresh_standalone_graph_claimed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
