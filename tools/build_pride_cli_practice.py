"""Stage CLI practice synchronization on the complete mixed-player candidate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-raster-state';native=ROOT/'build/pride-reset/fixed3'
    base_path=base/'build-report.json';original=bound(base_path)
    native_path=native/'build-report.json';build=bound(native_path)
    out=ROOT/'build/pride-cli-practice';out.mkdir(exist_ok=True)
    assert not (out/'build-report.json').exists(),'Preserve a completed build inventory'
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    target='tlk_scene_prepared_sdl';suffix=f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    host_source=ROOT/'build/pride-overlay/overlay-probe.c'
    stage=out/'unpatched/runner';stage.mkdir(parents=True,exist_ok=True)
    preprocessed=stage/'sdl_main.c';cmd=argv(row['command'])
    for flag,value in (('-c',host_source.as_posix()),('-o',preprocessed.as_posix()),('-MF',(out/'preprocess.d').as_posix()),('-MT','cli-practice')):cmd[cmd.index(flag)+1]=value
    cmd[cmd.index('-c')]='-E';cmd+=['-CC','-I'+str(ROOT/'tools'),'-DTLK_PRIVATE_COMPILED_HOOKS=1','-DTLK_FORCE_SCENE_PRESENTATION=1']
    with (out/'preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    patcher=ROOT/'engine/scripts/apply_runtime_patches.py';patches=ROOT/'engine/cmake/frontend-patches'
    subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',out/'unpatched','--out',out/'patched'],check=True,timeout=60)
    observer=ROOT/'tools/pride_cli_practice_probe.c';runs={};paths=[Path(__file__),base_path,native_path,host_source,observer,patcher,*sorted(patches.glob('*.hunks'))]
    # Pin every project dependency actually read by preprocessing, including
    # the unchanged coordinator and host source; generated .i files stay local.
    dependencies=(out/'preprocess.d').read_text().replace('\\\n',' ').split()[1:]
    for name in dependencies:
        p=Path(name);p=p if p.is_absolute() else cwd/p
        try:p.resolve().relative_to(ROOT)
        except ValueError:continue
        if p.is_file():paths.append(p.resolve())
    for variant,source in (('before',preprocessed),('after',out/'patched/sdl_main.c')):
        generated=out/(variant+'.i');generated.write_text(source.read_text()+'\n'+observer.read_text());paths.extend((source,generated))
        obj=out/(variant+'.obj');cmd=argv(row['command'])
        for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        with (out/(variant+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        response=argv('response '+(base/'sdl.rsp').read_text())[1:]
        replacements={str(base/'sdl-common_rtl.c.obj').replace('\\','/'):(native/'sdl-common_rtl.obj').as_posix(),
            'C:/TEMP2/lionKing/build/pride-restart-clock/sdl-bridge.obj':(native/'sdl-interp_bridge.obj').as_posix(),
            f'CMakeFiles/{target}.dir/runner/tlk_game.c.obj':(native/'sdl-tlk_game.obj').as_posix(),
            f'CMakeFiles/{target}.dir/runner/tlk_audio.c.obj':(native/'sdl-tlk_audio.obj').as_posix(),
            'C:/TEMP2/lionKing/build/pride-overlay/private-sdl-host.obj':obj.as_posix()}
        found=set()
        for i,a in enumerate(response):
            key=a.replace('\\','/')
            if key in replacements:response[i]=replacements[key];found.add(key)
        assert found==set(replacements),(found,set(replacements));response.append((native/'sdl-tlk_reset.obj').as_posix())
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
        cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(i for i,a in enumerate(cmd) if a.startswith('@'))
        rsp=out/(variant+'.rsp');rsp.write_text(subprocess.list2cmdline(response));cmd[index]='@'+rsp.as_posix();binary=out/(variant+'.exe');cmd[cmd.index('-o')+1]=binary.as_posix()
        for i,a in enumerate(cmd):
            if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/(variant+'.dll.a')).as_posix()
        cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame']
        with (out/(variant+'-link.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[variant]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print(variant,'mixed CLI player linked',flush=True)
    backend=ROOT/'build/pride-reset/audio-views2/genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name);paths.extend((backend,out/backend.name))
    report=dict(result='BUILT',runs=runs,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=build['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
