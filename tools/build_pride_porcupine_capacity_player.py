"""Expand the exhausted shared hook registry without changing execution logic."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-porcupine37';old=bound(prior/'build-report.json')
    out=ROOT/'build/pride-porcupine38';out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    source=ROOT/'build/pride-hook-capacity-runtime/interp_bridge.c'
    previous_source=cwd/'native-engine/tlk_pride_final_player_core-sources/runtime/interp_bridge.c'
    assert source.read_bytes().replace(b'kInterpPreOpcodeHookSlots = 512',b'kInterpPreOpcodeHookSlots = 192')==previous_source.read_bytes()
    key=next(p for p in old['link_inputs_sha256'] if p.endswith('runtime/interp_bridge.c.obj'))
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=cwd))
    entry=next(r for r in db if r.get('output','').replace('\\','/').endswith('tlk_pride_final_player_core.dir/tlk_pride_final_player_core-sources/runtime/interp_bridge.c.obj'))
    cmd=argv(entry['command']);obj=out/'interp-bridge.obj'
    for flag,value in [('-c',source),('-o',obj),('-MF',out/'interp-bridge.d'),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    index=next(i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==ROOT/key)
    inputs[index]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',source,previous_source,ROOT/'engine/cmake/runtime-patches/zz-pride-hook-capacity.hunks']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'interp-bridge':cmd},
                fresh_standalone_graph_claimed=False,only_runtime_source_change='kInterpPreOpcodeHookSlots 192 to512',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
