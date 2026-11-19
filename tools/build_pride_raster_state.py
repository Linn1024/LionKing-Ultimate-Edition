"""Link the practice/overlay hosts with complete native raster rollback state."""
import json
from pathlib import Path
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-overlay';out=ROOT/'build/pride-raster-state';out.mkdir(exist_ok=True)
    original_path=base/'build-report.json';original=bound(original_path)
    for name,sha in original['production_sha256'].items():assert digest(ROOT/name)==sha,name
    patches=ROOT/'engine/cmake/runtime-patches';runtime=out/'runtime'
    subprocess.run([sys.executable,ROOT/'engine/scripts/apply_runtime_patches.py','--patches',patches,
        '--snesrecomp',ROOT/'engine/snesrecomp','--out',runtime],cwd=ROOT,check=True,timeout=60)
    unchanged={}
    for path in runtime.iterdir():
        if path.suffix in ('.c','.h') and path.name not in ('common_rtl.c','ppu.c'):
            old=ROOT/'build/pride-restart-clock/runtime'/path.name
            assert old.exists() and digest(path)==digest(old),path.name
            unchanged[path.name]=digest(path)
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));runs={}
    sources=[Path(__file__),original_path,ROOT/'engine/scripts/apply_runtime_patches.py',
        ROOT/'engine/snesrecomp/runner/src/snes/ppu.c',runtime/'common_rtl.c',runtime/'ppu.c',*sorted(patches.glob('*.hunks'))]
    for host in ('probe','sdl'):
        for name,sha in original['runs'][host]['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        target='tlk_scene_prepared_'+host;replacements={}
        for source,suffix in (('common_rtl.c',f'CMakeFiles/{target}.dir/tlk-runtime/common_rtl.c.obj'),
                              ('ppu.c',f'CMakeFiles/{target}.dir/snesrecomp/runner/src/snes/ppu.c.obj')):
            row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
            obj=out/(host+'-'+source+'.obj');command=argv(row['command'])
            for flag,value in (('-c',(runtime/source).as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
                command[command.index(flag)+1]=value
            with (out/(host+'-'+source+'-compile.log')).open('wb') as log:
                subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            replacements[suffix]=obj.as_posix()
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());i=next(n for n,a in enumerate(command) if a.startswith('@'))
        response=argv('response '+(base/(host+'.rsp')).read_text())[1:];found=set()
        for n,a in enumerate(response):
            if a.replace('\\','/') in replacements:
                found.add(a.replace('\\','/'));response[n]=replacements[a.replace('\\','/')]
        assert found==set(replacements)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                path=Path(a);path=path if path.is_absolute() else cwd/path
                inputs[str(path.resolve().relative_to(ROOT)).replace('\\','/')]=digest(path)
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response));command[i]='@'+rsp.as_posix()
        binary=out/('raster-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        command+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load']
        with (out/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
        runs[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print(host,'raster state linked',flush=True)
    report=dict(result='BUILT',scope=__doc__,runs=runs,unchanged_runtime_sha256=unchanged,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        production_sha256=original['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
