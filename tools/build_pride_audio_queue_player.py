"""Recompile only the final host for device queue observation and priming work."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='build/pride-audio-queue27');args=parser.parse_args()
    prior=ROOT/'build/pride-restart-difficulty25';old=bound(prior/'build-report.json')
    out=ROOT/args.output;out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    original=cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
                    '--snesrecomp',str(original),'--out',str(out/'frontend')],check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copyfile(original/name,out/'frontend'/name)
    cmd=old['compiles']['host'].copy();obj=out/'host.obj'
    for flag,value in [('-o',obj),('-MF',out/'host.d'),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
    i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
    with (out/'host-compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:];inputs[inputs.index((prior/'host.obj').as_posix())]=obj.as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',out/'frontend/sdl_main.c',ROOT/'engine/runner/pride/pride_present.inc',
           *sorted((ROOT/'engine/cmake/final-frontend-patches').glob('*.hunks'))]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'host':cmd},
                fresh_standalone_graph_claimed=False,game_objects_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
