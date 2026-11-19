"""Build plain native hosts with the clock and raster snapshot repairs."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-raster-state';out=base/'native';out.mkdir(exist_ok=True)
    build_path=base/'build-report.json';build=bound(build_path)
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));results={}
    for host in ('headless','sdl'):
        target='tlk_'+host;replacements={}
        for source,suffix in (('interp_bridge.c',f'CMakeFiles/{target}.dir/tlk-runtime/interp_bridge.c.obj'),
                              ('common_rtl.c',f'CMakeFiles/{target}.dir/tlk-runtime/common_rtl.c.obj'),
                              ('ppu.c',f'CMakeFiles/{target}.dir/snesrecomp/runner/src/snes/ppu.c.obj')):
            entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
            obj=out/(host+'-'+source+'.obj');command=argv(entry['command'])
            for flag,value in (('-c',(base/'runtime'/source).as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
                command[command.index(flag)+1]=value
            with (out/(host+'-'+source+'-compile.log')).open('wb') as log:
                subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            replacements[suffix]=obj.as_posix()
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());i=next(n for n,a in enumerate(command) if a.startswith('@'))
        if '&&' in command:command=command[:command.index('&&')]
        lines=(cwd/'build.ninja').read_text().splitlines()
        edge=next(n for n,line in enumerate(lines) if line.startswith('build '+target+'.exe: '))
        inputs=lines[edge].split(': ',1)[1].split(' ',1)[1].split(' |',1)[0];values={}
        for line in lines[edge+1:]:
            if not line.strip():break
            key,value=line.strip().split(' = ',1);values[key]=value
        assert not values.get('LINK_PATH',''),values.get('LINK_PATH')
        response=argv('response '+inputs+' '+values['LINK_LIBRARIES'])[1:];found=set()
        for n,a in enumerate(response):
            key=a.replace('\\','/')
            if key in replacements:response[n]=replacements[key];found.add(key)
        assert found==set(replacements)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                path=Path(a);path=path if path.is_absolute() else cwd/path
                inputs[str(path.resolve().relative_to(ROOT)).replace('\\','/')]=digest(path)
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[i]='@'+rsp.as_posix()
        binary=out/('native-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        with (out/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        results[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print('Native',host,'raster linked',flush=True)
    paths=(Path(__file__),build_path,ROOT/'engine/runner/tlk_savestate.c')
    report=dict(result='BUILT',runs=results,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        production_sha256=build['production_sha256'],public_player_enabled=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
