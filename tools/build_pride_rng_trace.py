"""Build a read-only LLE RNG observer without replacing installed executables."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    out=ROOT/'build/pride-rng-lifecycle';out.mkdir(exist_ok=True);assert not (out/'build-report.json').exists();cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));source=ROOT/'tools/pride_rng_native_trace.c'
    key='CMakeFiles/tlk_headless.dir/runner/headless_main.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==key);obj=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    raw=subprocess.check_output([ninja,'-t','commands','tlk_headless.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());at=next(i for i,a in enumerate(cmd) if a.startswith('@'))
    # Ninja removes its transient rsp after a successful link. Read the explicit
    # ordered objects/libraries from its generated rule without rebuilding it.
    graph=(cwd/'build.ninja').read_text();start=graph.index('build tlk_headless.exe:');end=graph.index('\n\n',start);block=graph[start:end]
    (out/'link-rule.txt').write_text(block+'\n')
    objects=block.splitlines()[0].split(' ',3)[3].split(' |',1)[0]
    libraries=next(line.split(' = ',1)[1] for line in block.splitlines() if line.startswith('  LINK_LIBRARIES = '))
    response=argv('response '+(objects+' '+libraries).replace('$:',':').replace('$ ',' '))[1:]
    assert response.count(key)==1;response[response.index(key)]=obj.as_posix()
    rsp=out/'observer.rsp';rsp.write_text(subprocess.list2cmdline(response));cmd[at]='@'+rsp.as_posix();binary=out/'observer.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'observer.dll.a').as_posix()
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[p.resolve().relative_to(ROOT).as_posix()]=digest(p)
    paths=[Path(__file__),source,ROOT/'engine/runner/headless_main.c',out/'link-rule.txt']
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},installed_headless_sha256=digest(cwd/'tlk_headless.exe'),production_changed=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Read-only original RNG observer built',flush=True)


if __name__=='__main__':main()
