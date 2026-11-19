"""Build plain reset-lifecycle candidates and the unchanged native observer."""
import json
from pathlib import Path
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-raster-state/native';out=ROOT/'build/pride-reset/fixed';out.mkdir(parents=True,exist_ok=True)
    base_path=base/'build-report.json';base_report=bound(base_path)
    before_path=ROOT/'build/pride-reset/before/build-report.json';before=bound(before_path)
    for name,sha in base_report['production_sha256'].items():assert digest(ROOT/name)==sha,name
    patcher=ROOT/'engine/scripts/apply_runtime_patches.py'
    for patches,root,destination in ((ROOT/'engine/cmake/runtime-patches',ROOT/'engine/snesrecomp',out/'runtime'),
                                    (ROOT/'engine/cmake/game-patches',ROOT/'engine',out/'game')):
        subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',root,'--out',destination],cwd=ROOT,check=True,timeout=60)
    for path in (out/'runtime').iterdir():
        if path.suffix in ('.c','.h') and path.name not in ('common_rtl.c','interp_bridge.c'):
            old=ROOT/'build/pride-raster-state/runtime'/path.name
            assert old.exists() and digest(path)==digest(old),path.name
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    runs={};responses={}
    for host in ('headless','sdl'):
        target='tlk_'+host;replacements={}
        for name,source,old in (
            ('interp_bridge',out/'runtime/interp_bridge.c',base/(host+'-interp_bridge.c.obj')),
            ('common_rtl',out/'runtime/common_rtl.c',base/(host+'-common_rtl.c.obj')),
            ('tlk_game',out/'game/tlk_game.c',None),('tlk_audio',out/'game/tlk_audio.c',None),
            ('tlk_reset',ROOT/'engine/runner/tlk_reset.c',None)):
            runtime=name in ('interp_bridge','common_rtl');suffix=f'CMakeFiles/{target}.dir/'+('tlk-runtime/' if runtime else 'runner/')+(name if name!='tlk_reset' else 'tlk_game')+'.c.obj'
            entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
            obj=out/(host+'-'+name+'.obj');command=argv(entry['command'])
            for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
                command[command.index(flag)+1]=value
            with (out/(host+'-'+name+'-compile.log')).open('wb') as log:
                subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            if name!='tlk_reset':replacements[old.as_posix() if old else suffix]=obj.as_posix()
            else:extra=obj
        response=argv('response '+(base/(host+'.rsp')).read_text())[1:];found=set()
        for n,arg in enumerate(response):
            key=arg.replace('\\','/')
            if key in replacements:response[n]=replacements[key];found.add(key)
        assert found==set(replacements),(found,set(replacements));response.append(extra.as_posix());responses[host]=response
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(n for n,a in enumerate(command) if a.startswith('@'))
        if '&&' in command:command=command[:command.index('&&')]
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[index]='@'+rsp.as_posix()
        binary=out/('native-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        with (out/(host+'-link.log')).open('wb') as log:subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        if host=='headless':observer_command=list(command)
        print('Reset native',host,'linked',flush=True)
    response=list(responses['headless']);host_key='CMakeFiles/tlk_headless.dir/runner/headless_main.c.obj'
    observer_obj=ROOT/'build/pride-reset/before/reset-host.obj';assert digest(observer_obj)==before['link_inputs_sha256'][str(observer_obj.relative_to(ROOT)).replace('\\','/')]
    assert response.count(host_key)==1;response[response.index(host_key)]=observer_obj.as_posix()
    rsp=out/'probe.rsp';rsp.write_text(subprocess.list2cmdline(response));index=next(n for n,a in enumerate(observer_command) if a.startswith('@'));observer_command[index]='@'+rsp.as_posix()
    binary=out/'reset-probe.exe';observer_command[observer_command.index('-o')+1]=binary.as_posix()
    with (out/'probe-link.log').open('wb') as log:subprocess.run(observer_command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=dict(runs['headless']['link_inputs_sha256']);del inputs['engine/build-win/'+host_key]
    inputs[str(observer_obj.relative_to(ROOT)).replace('\\','/')]=digest(observer_obj)
    paths=[Path(__file__),base_path,before_path,patcher,ROOT/'engine/runner/tlk_reset.c',ROOT/'engine/runner/tlk_reset.h',
           *sorted((ROOT/'engine/cmake/runtime-patches').glob('*.hunks')),*sorted((ROOT/'engine/cmake/game-patches').glob('*.hunks')),
           *sorted((out/'runtime').glob('*.c')),*sorted((out/'game').glob('*.c'))]
    report=dict(result='BUILT',runs=runs,binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        production_sha256=base_report['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
