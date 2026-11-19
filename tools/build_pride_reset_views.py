"""Native48kHz headless and real-window observers for machine reset tests."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-reset/fixed';build_path=base/'build-report.json';build=bound(build_path)
    out=ROOT/'build/pride-reset/views';out.mkdir(exist_ok=True)
    source_path=ROOT/'tools/pride_reset_probe.c';original=source_path.read_text()
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));runs={};paths=[Path(__file__),build_path,source_path]
    for host in ('headless','sdl'):
        target='tlk_'+host;source=original
        old='#include "../engine/runner/headless_main.c"';assert source.count(old)==1
        source=source.replace(old,'#include "'+(ROOT/f'engine/runner/{host}_main.c').as_posix()+'"')
        source=source.replace('reset_ready=1;','reset_ready=1; RtlSetAudioOutputRate(48000);')
        source=source.replace('else exit(91);','else if(strcmp(kind,"none"))exit(91);')
        if host=='sdl':
            source=source.replace('InputForFrame(i)','TapeFrame(i)').replace('bool result=TlkWideEndFrame(pixels);reset_drain(reset_pcm);','bool result=TlkWideEndFrame(pixels);')
        generated=out/(host+'-probe.c');generated.write_text(source);paths.extend((generated,ROOT/f'engine/runner/{host}_main.c'))
        suffix=f'CMakeFiles/{target}.dir/runner/{host}_main.c.obj';entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        obj=out/(host+'-host.obj');command=argv(entry['command'])
        for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        with (out/(host+'-compile.log')).open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        response=argv('response '+(base/(host+'.rsp')).read_text())[1:];assert response.count(suffix)==1;response[response.index(suffix)]=obj.as_posix()
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(n for n,a in enumerate(command) if a.startswith('@'))
        if '&&' in command:command=command[:command.index('&&')]
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[index]='@'+rsp.as_posix()
        binary=out/(host+'-reset.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        with (out/(host+'-link.log')).open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print(host,'reset observer linked',flush=True)
    report=dict(result='BUILT',runs=runs,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=build['production_sha256'])
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
