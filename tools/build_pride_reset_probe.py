"""Link a native reset observer without replacing established binaries."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-raster-state/native';out=ROOT/'build/pride-reset/before';out.mkdir(parents=True,exist_ok=True)
    build_path=base/'build-report.json';build=bound(build_path)
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['runs']['headless']['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_headless'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));suffix=f'CMakeFiles/{target}.dir/runner/headless_main.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    obj=out/'reset-host.obj';command=argv(row['command'])
    for flag,value in (('-c',(ROOT/'tools/pride_reset_probe.c').as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
        command[command.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(n for n,a in enumerate(command) if a.startswith('@'))
    if '&&' in command:command=command[:command.index('&&')]
    response=argv('response '+(base/'headless.rsp').read_text())[1:];assert response.count(suffix)==1
    response[response.index(suffix)]=obj.as_posix();rsp=out/'probe.rsp';rsp.write_text(subprocess.list2cmdline(response));command[index]='@'+rsp.as_posix()
    binary=out/'reset-probe.exe';command[command.index('-o')+1]=binary.as_posix()
    for n,a in enumerate(command):
        if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/'probe.dll.a').as_posix()
    with (out/'link.log').open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            path=Path(a);path=path if path.is_absolute() else cwd/path
            inputs[str(path.resolve().relative_to(ROOT)).replace('\\','/')]=digest(path)
    paths=(Path(__file__),ROOT/'tools/pride_reset_probe.c',ROOT/'engine/runner/headless_main.c',build_path)
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=build['production_sha256'])
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Reset observer linked',flush=True)


if __name__=='__main__':main()
