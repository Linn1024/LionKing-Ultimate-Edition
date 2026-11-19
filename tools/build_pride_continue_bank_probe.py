"""Build the private Continue cache controller with the maintained bank API."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-continue-bank-probe2';out.mkdir()
    prior=ROOT/'build/pride-continue-fast-reload-probe'
    bound(prior/'build-report.json')
    build=ROOT/'build/pride-title-work/player'
    public=ROOT/'build/pride-arena-work/tlk_pride_player.exe';before=digest(public)
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    host=next(r for r in db if r.get('file','').endswith('/pride/tlk_pride_host.c'))
    bank=next(r for r in db if r.get('file','').endswith('/tlk_native_bank.c') and '/tlk_pride_player.dir/' in r['output'])
    shutil.copytree(prior/'frontend',out/'frontend')
    source=out/'host.c'
    fast=prior/'fast.c'
    source.write_text('#include <stdint.h>\nvoid FinalSceneCaptureNative(const uint8_t*);\n'
        'void FinalScenePaintNative(uint32_t*);\n#define __wrap_RtlRunFrame PrideObservedRunFrame\n'
        '#include "'+(ROOT/'engine/runner/pride/tlk_pride_host.c').as_posix()+'"\n'
        '#undef __wrap_RtlRunFrame\n#include "'+fast.as_posix()+'"\n'
        '#include "'+(ROOT/'tools/pride_continue_bank_probe.c').as_posix()+'"\n')
    objects={}
    for name,entry,src in [('host',host,source),('bank',bank,ROOT/'engine/runner/tlk_native_bank.c')]:
        cmd=argv(entry['command']);obj=out/(name+'.obj')
        for flag,value in [('-c',src),('-o',obj),('-MF',out/(name+'.d')),('-MT',obj)]:
            cmd[cmd.index(flag)+1]=str(value)
        if name=='host':
            index=next(n for n,s in enumerate(cmd) if s.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[index]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
            cmd+=['-I'+str(ROOT/'tools')]
        with (out/(name+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        objects[entry['output']]=obj.as_posix()
    lines=(build/'build.ninja').read_text().splitlines()
    start=next(n for n,s in enumerate(lines) if s.startswith('build native-engine/tlk_pride_player.exe:'))
    inputs=lines[start].split(': ',1)[1].split(' ',1)[1].split(' |')[0].split()
    for old,new in objects.items():assert inputs.count(old)==1;inputs[inputs.index(old)]=new
    libraries=next(s.split(' = ',1)[1] for s in lines[start+1:] if s.startswith('  LINK_LIBRARIES ='))
    inputs+=argv('link '+libraries)[1:]
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs));binary=out/'player.exe'
    cmd=['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
        '@'+str(rsp),'-o',str(binary)]
    with (out/'link.log').open('wb') as log:
        subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    assert digest(public)==before
    paths=[Path(__file__),source,fast,prior/'build-report.json',ROOT/'tools/pride_continue_bank_probe.c',
        ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/runner/tlk_native_bank.h',
        ROOT/'tools/pride_final_scene_probe.c',ROOT/'tools/pride_final_skip_probe.c']
    report=dict(result='BUILT',binary_sha256=digest(binary),public_player_unchanged=True,
        interpreter_only_experiment=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix():digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
