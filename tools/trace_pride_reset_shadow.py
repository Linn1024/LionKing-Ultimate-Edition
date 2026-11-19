"""Observe real FastROM/HDMA shadows before/after the current reset APIs."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);args=p.parse_args()
    base=ROOT/args.base;build_path=base/'build-report.json';build=bound(build_path);out=base/'shadow';out.mkdir()
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    row=next(r for r in db if r.get('output','').replace('\\','/')=='CMakeFiles/tlk_headless.dir/runner/tlk_game.c.obj')
    obj=out/'shadow.obj';source=ROOT/'tools/pride_reset_shadow.c';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    subprocess.run(cmd,cwd=cwd,check=True,timeout=90)
    raw=subprocess.check_output([ninja,'-t','commands','tlk_headless.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(i for i,a in enumerate(cmd) if a.startswith('@'))
    if '&&' in cmd:cmd=cmd[:cmd.index('&&')]
    response=argv('response '+(base/'probe.rsp').read_text())[1:]+[obj.as_posix()]
    rsp=out/'shadow.rsp';rsp.write_text(subprocess.list2cmdline(response));cmd[index]='@'+rsp.as_posix();binary=out/'shadow.exe';cmd[cmd.index('-o')+1]=binary.as_posix();cmd+=['-Wl,--wrap=RtlReset,--wrap=SnesInit']
    subprocess.run(cmd,cwd=cwd,check=True,timeout=90)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n');observations={};commands={}
    for kind in ('soft','init'):
        folder=out/kind;folder.mkdir();command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--input',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape','--frames',1,'--wide',256]
        env=os.environ.copy();env.update(TLK_RESET_PROBE=str(folder),TLK_RESET_KIND=kind,TLK_RESET_WARM='1211',TLK_RESET_ONLY='1');commands[kind]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[kind],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        assert r.returncode==0
        observations[kind]=[dict(kind=k,stage=s,memsel=int(m),hdma=int(h)) for k,s,m,h in re.findall(r'reset_shadow,(\w+),(\w+),(\d+),(\d+)',(folder/'run.log').read_text())]
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    paths=(Path(__file__),source,build_path)
    report=dict(result='OBSERVED',observations=observations,commands=commands,binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(observations,flush=True)

if __name__=='__main__':main()
