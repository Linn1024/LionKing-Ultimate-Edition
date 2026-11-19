"""Build ordinary native hosts with only the fractional-clock snapshot repair."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    base=ROOT/'build/pride-restart-clock';out=base/'native';out.mkdir(exist_ok=True)
    build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));results={}
    for host in ('headless','sdl'):
        target='tlk_'+host;suffix='CMakeFiles/'+target+'.dir/tlk-runtime/interp_bridge.c.obj'
        entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        obj=out/(host+'-bridge.obj');command=argv(entry['command'])
        for flag,value in (('-c',(base/'runtime/interp_bridge.c').as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        with (out/(host+'-compile.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());i=next(n for n,a in enumerate(command) if a.startswith('@'))
        if '&&' in command:command=command[:command.index('&&')]
        # Ninja normally deletes its transient native-target response file.
        # Reconstruct the same explicit objects and LINK_LIBRARIES from its
        # generated link edge; do not trigger a production rebuild to retain it.
        lines=(cwd/'build.ninja').read_text().splitlines()
        edge=next(n for n,line in enumerate(lines) if line.startswith('build '+target+'.exe: '))
        inputs=lines[edge].split(': ',1)[1].split(' ',1)[1].split(' |',1)[0]
        values={}
        for line in lines[edge+1:]:
            if not line.strip():break
            key,value=line.strip().split(' = ',1);values[key]=value
        assert not values.get('LINK_PATH',''),values.get('LINK_PATH')
        response=argv('response '+inputs+' '+values['LINK_LIBRARIES'])[1:];count=0
        for n,a in enumerate(response):
            if a.replace('\\','/')==suffix:response[n]=obj.as_posix();count+=1
        assert count==1
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else cwd/p
                inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[i]='@'+rsp.as_posix()
        binary=out/('native-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        with (out/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        results[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print('Native',host,'linked',flush=True)
    paths=(Path(__file__),build_path,ROOT/'engine/runner/tlk_savestate.c')
    report=dict(result='BUILT',runs=results,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        production_sha256=build['production_sha256'],public_player_enabled=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
