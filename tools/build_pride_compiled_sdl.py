"""Link a private SDL host to verified isolated compiled hook objects."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    out=ROOT/'build/pride-compiled-revival';folder=ROOT/'engine/build-win'
    report_path=out/'build-report.json';report=json.loads(report_path.read_text())
    for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in report['object_sha256'].items():assert digest(out/'objects'/name)==sha,name
    for name,sha in report['production_sha256'].items():assert digest(ROOT/name)==sha,name
    ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_restore_sdl.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=folder))
    suffix='CMakeFiles/tlk_scene_restore_sdl.dir/C_/TEMP2/lionKing/tools/pride_scene_restore_probe.c.obj'
    entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    obj=out/'objects/private-sdl-host.obj';command=argv(entry['command'])
    for flag,value in (('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
        command[command.index(flag)+1]=value
    command+=['-I'+str(ROOT/'tools'),'-DTLK_PRIVATE_COMPILED_HOOKS=1']
    with (out/'sdl-compile.log').open('wb') as log:
        subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    link=subprocess.check_output([ninja,'-t','commands',target],cwd=folder,text=True).splitlines()[-1]
    assert link.count('&&')==2
    command=argv(link.split('&&',1)[1].rsplit('&&',1)[0].strip())
    index=next(n for n,a in enumerate(command) if a.startswith('@'))
    response=argv('response '+(folder/command[index][1:]).read_text())[1:]
    generation=json.loads((out/'generation-report.json').read_text())
    replacements={'CMakeFiles/snesrecomp_game.dir/generated/snesrecomp/'+name+'.obj':
                  (out/'objects'/(name+'.obj')).as_posix() for name in generation['instrumented_units']}
    replacements[suffix]=obj.as_posix();replaced=set()
    for n,arg in enumerate(response):
        key=arg.replace('\\','/')
        if key in replacements:response[n]=replacements[key];replaced.add(key)
    assert replaced==set(replacements)
    rsp=out/'compiled-restore-sdl.rsp';rsp.write_text(subprocess.list2cmdline(response))
    command[index]='@'+rsp.as_posix();binary=out/'compiled-restore-sdl.exe'
    command[command.index('-o')+1]=binary.as_posix()
    for n,arg in enumerate(command):
        if arg.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/'compiled-restore-sdl.dll.a').as_posix()
    with (out/'sdl-link.log').open('wb') as log:
        subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name,sha in report['production_sha256'].items():assert digest(ROOT/name)==sha,name
    (out/'sdl-build-report.json').write_text(json.dumps(dict(result='BUILT',
        binary_sha256=digest(binary),headless_build_report_sha256=digest(report_path),
        script_sha256=digest(Path(__file__)),host_object_sha256=digest(obj),
        primary_binaries_unchanged=True,compiled_ownership_verified=False),indent=2)+'\n')
    print('Isolated compiled SDL host linked; primary binaries unchanged',flush=True)


if __name__=='__main__':main()
