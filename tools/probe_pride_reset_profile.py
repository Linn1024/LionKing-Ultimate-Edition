"""Exercise unchanged audio-profile apply after actual cold and warm resets."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--expect-change',action='store_true')
    args=parser.parse_args()
    base=ROOT/args.base;build_path=base/'build-report.json';build=bound(build_path)
    out=base/'profile-noop';out.mkdir()
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    row=next(r for r in db if r.get('output','').replace('\\','/')=='CMakeFiles/tlk_headless.dir/runner/tlk_game.c.obj')
    source=ROOT/'tools/pride_reset_profile_probe.c';obj=out/'profile.obj';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    subprocess.run(cmd,cwd=cwd,check=True,timeout=90)
    raw=subprocess.check_output([ninja,'-t','commands','tlk_headless.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    if '&&' in cmd:cmd=cmd[:cmd.index('&&')]
    response=argv('response '+(base/'probe.rsp').read_text())[1:]+[obj.as_posix()]
    rsp=out/'profile.rsp';rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'))
    cmd[index]='@'+rsp.as_posix();binary=out/'profile.exe';cmd[cmd.index('-o')+1]=binary.as_posix();cmd+=['-Wl,--wrap=TlkResetMachine']
    subprocess.run(cmd,cwd=cwd,check=True,timeout=90)
    backend=ROOT/'build/pride-reset/audio-views2/genesis_plus_gx_libretro.dll'
    backend_build=ROOT/'build/pride-reset/audio-views2/build-report.json';bound(backend_build)
    shutil.copy2(backend,out/backend.name)
    author=ROOT/'build/pride-source-live/seeded/resources.ini'
    audio=''.join(line+'\n' for line in author.read_text().splitlines() if line.startswith('audio.') and line.endswith('= md'))
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    checks={};observations={};commands={}
    for selected in ('native','md'):
        profile=out/(selected+'.ini');profile.write_text('schema = 1\ngame = snes\n'+(audio if selected=='md' else ''))
        for kind in ('soft','init'):
            for mode in ('aot','lle'):
                name=f'{selected}-{kind}-{mode}';folder=out/name;folder.mkdir()
                command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--input',tape,'--frames',1,'--wide',256]
                if mode=='lle':command+=['--lle']
                env=os.environ.copy();env.update(TLK_RESET_PROBE=str(folder),TLK_RESET_KIND=kind,TLK_RESET_WARM='1211',TLK_RESET_ONLY='1')
                commands[name]=list(map(str,command))
                with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
                assert not r.returncode,name
                log=(folder/'run.log').read_text();assert 'Profile rejected' not in log and 'MD sound library unavailable' not in log,name
                values=list(map(int,re.findall(r'reset_profile_noop,(\d+)',log)));observations[name]=values
                checks[name+'/two_resets_observed']=len(values)==2
                checks[name+'/unchanged_apply']=values==[0,0]
                print(name,values,flush=True)
    expected=all(v for k,v in checks.items() if not k.endswith('/unchanged_apply')) and all(values==([1,1] if name.startswith('md-') else [0,0]) for name,values in observations.items())
    result='REPRODUCED' if args.expect_change and expected else 'PASS' if all(checks.values()) else 'INCOMPLETE'
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    paths=[Path(__file__),source,build_path,backend_build,backend,author,tape]
    report=dict(result=result,checks=checks,observations=observations,commands=commands,binary_sha256=digest(binary),link_inputs_sha256=inputs,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result,flush=True)
    if result not in ('PASS','REPRODUCED'):raise SystemExit(1)


if __name__=='__main__':main()
