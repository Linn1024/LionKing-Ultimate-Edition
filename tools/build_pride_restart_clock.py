"""Link the restart candidate with restored fractional APU timing residue."""
import json
from pathlib import Path
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    base=ROOT/'build/pride-restart';out=ROOT/'build/pride-restart-clock';out.mkdir(exist_ok=True)
    original_path=base/'build-report.json';original=json.loads(original_path.read_text())
    for name,sha in original['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in original['production_sha256'].items():assert digest(ROOT/name)==sha,name
    patch_dir=ROOT/'engine/cmake/runtime-patches';runtime=out/'runtime'
    subprocess.run([sys.executable,ROOT/'engine/scripts/apply_runtime_patches.py','--patches',patch_dir,
        '--snesrecomp',ROOT/'engine/snesrecomp','--out',runtime],cwd=ROOT,check=True,timeout=60)
    unchanged={}
    for p in runtime.iterdir():
        q=ROOT/'engine/build-win/tlk-runtime'/p.name
        if p.suffix in ('.c','.h') and p.name!='interp_bridge.c':
            assert q.exists() and digest(p)==digest(q),p.name
            unchanged[p.name]=digest(p)
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));runs={}
    sources=[Path(__file__),original_path,ROOT/'engine/scripts/apply_runtime_patches.py',
        ROOT/'engine/snesrecomp/runner/src/snes/interp_bridge.c',runtime/'interp_bridge.c',*sorted(patch_dir.glob('*.hunks'))]
    for host in ('probe','sdl'):
        for name,sha in original['runs'][host]['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        target='tlk_scene_prepared_'+host
        suffix='CMakeFiles/'+target+'.dir/tlk-runtime/interp_bridge.c.obj'
        row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        obj=out/(host+'-bridge.obj');command=argv(row['command'])
        for flag,value in (('-c',(runtime/'interp_bridge.c').as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        with (out/(host+'-compile.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());i=next(n for n,a in enumerate(command) if a.startswith('@'))
        response=argv('response '+(base/(host+'.rsp')).read_text())[1:];count=0
        for n,a in enumerate(response):
            if a.replace('\\','/')==suffix:response[n]=obj.as_posix();count+=1
        assert count==1
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else cwd/p
                inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[i]='@'+rsp.as_posix()
        binary=out/('restart-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        command+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load']
        with (out/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        runs[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print(host,'fractional clock candidate linked',flush=True)
    report=dict(result='BUILT',scope=__doc__,runs=runs,unchanged_runtime_sources_sha256=unchanged,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        production_sha256=original['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
