"""Build the maintained arena-entry repair with the pinned preview link inputs.

Only the host object is replaced. No generated object, public binary or
framework source is changed.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    out=ROOT/'build/pride-arena-work';out.mkdir()
    build=ROOT/'build/pride-title-work/player';ninja='C:/mingw32/bin/ninja.exe'
    public=build/'native-engine/tlk_pride_player.exe';before=digest(public)
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=build))
    entry=next(r for r in db if r.get('file','').endswith('/pride/tlk_pride_host.c'))
    command=argv(entry['command']);obj=out/'host.obj'
    for flag,value in [('-o',obj),('-MF',out/'host.d'),('-MT',obj)]:command[command.index(flag)+1]=str(value)
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
    binary=out/'tlk_pride_player.exe'
    link=['C:/mingw32/bin/g++.exe','-O3','-static',
          '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
          '@'+str(rsp),'-o',str(binary)]
    with (out/'link.log').open('wb') as log:
        subprocess.run(link,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):
        shutil.copyfile(build/'native-engine'/name,out/name)
    assert digest(public)==before
    sources=[Path(__file__),ROOT/'build/pride-arena-baseline/report.json',build/'build.ninja']
    sources+=list((ROOT/'engine/runner/pride').rglob('*.c'))+list((ROOT/'engine/runner/pride').rglob('*.h'))+list((ROOT/'engine/runner/pride').rglob('*.inc'))
    link_inputs={str((build/p).resolve().relative_to(ROOT)).replace('\\','/'):digest(build/p) for p in inputs if not p.startswith('-')}
    report=dict(result='BUILT',binary_sha256=digest(binary),public_player_unchanged=True,compile=command,link=link,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},link_inputs_sha256=link_inputs)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Maintained arena candidate',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
