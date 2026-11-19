"""Link an isolated final-life preparation experiment from pinned current objects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    out=ROOT/'build/pride-final-display-probe2';out.mkdir()
    build=ROOT/'build/pride-title-work/player';ninja='C:/mingw32/bin/ninja.exe'
    public=ROOT/'build/pride-arena-work/tlk_pride_player.exe';before=digest(public)
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=build))
    entry=next(r for r in db if r.get('file','').endswith('/pride/tlk_pride_host.c'))
    source=out/'host.c';source.write_text('#define __wrap_RtlRunFrame PrideObservedRunFrame\n#include "'+
        (ROOT/'engine/runner/pride/tlk_pride_host.c').as_posix()+'"\n#undef __wrap_RtlRunFrame\n#include "'+
        (ROOT/'tools/pride_final_display_probe.c').as_posix()+'"\n')
    command=argv(entry['command']);obj=out/'host.obj'
    for flag,value in [('-c',source),('-o',obj),('-MF',out/'host.d'),('-MT',obj)]:command[command.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    lines=(build/'build.ninja').read_text().splitlines()
    start=next(n for n,s in enumerate(lines) if s.startswith('build native-engine/tlk_pride_player.exe:'))
    objects=lines[start].split(': ',1)[1].split(' ',1)[1].split(' |')[0].split()
    assert objects.count(entry['output'])==1
    objects[objects.index(entry['output'])]=obj.as_posix()
    libraries=next(s.split(' = ',1)[1] for s in lines[start+1:] if s.startswith('  LINK_LIBRARIES ='))
    inputs=objects+argv('link '+libraries)[1:]
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    binary=out/'player.exe'
    link=['C:/mingw32/bin/g++.exe','-O3','-static',
          '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
          '@'+str(rsp),'-o',str(binary)]
    with (out/'link.log').open('wb') as log:
        subprocess.run(link,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(ROOT/'build/pride-arena-work/genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    assert digest(public)==before
    paths=[Path(__file__),source,ROOT/'tools/pride_final_display_probe.c',ROOT/'tools/pride_final_skip_late_probe.c',ROOT/'tools/pride_final_skip_probe.c',ROOT/'engine/runner/pride/tlk_pride_host.c',ROOT/'engine/runner/pride/pride_repeat_owner.c']
    report=dict(result='BUILT',binary_sha256=digest(binary),public_player_unchanged=True,interpreter_only_experiment=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        link_inputs_sha256={str((build/p).resolve().relative_to(ROOT)).replace('\\','/'):digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Final display preparation probe built',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
