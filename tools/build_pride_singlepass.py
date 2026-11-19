"""Stage one-pass host overlays while retaining the verified mixed reset core."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-machine-player4';base_path=base/'build-report.json';original=bound(base_path)
    out=ROOT/'build/pride-singlepass';out.mkdir(exist_ok=True)
    assert not (out/'build-report.json').exists(),'Preserve completed builds'
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));suffix=f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    patcher=ROOT/'engine/scripts/apply_runtime_patches.py';patches=ROOT/'engine/cmake/frontend-patches'
    subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',ROOT/'engine','--out',out/'patched'],check=True,timeout=60)
    patched=out/'patched/sdl_main.c';cloned={}
    def clone(path):
        path=path.resolve()
        if path==ROOT/'engine/runner/sdl_main.c':return patched
        try:relative=path.relative_to(ROOT/'tools')
        except ValueError:return path
        if path in cloned:return cloned[path]
        destination=out/'include'/relative;cloned[path]=destination;destination.parent.mkdir(parents=True,exist_ok=True)
        def include(match):
            dependency=path.parent/match.group(1)
            return '#include "'+clone(dependency).as_posix()+'"' if dependency.is_file() else match.group(0)
        destination.write_text(re.sub(r'#include\s+"([^"\n]+)"',include,path.read_text()))
        return destination
    original_host=ROOT/'tools/pride_practice_probe.c';host_source=clone(original_host)
    stage=out/'preprocessed';stage.mkdir(exist_ok=True);preprocessed=stage/'host.i'
    cmd=argv(row['command'])
    for flag,value in (('-c',host_source.as_posix()),('-o',preprocessed.as_posix()),('-MF',(out/'preprocess.d').as_posix()),('-MT','singlepass')):cmd[cmd.index(flag)+1]=value
    cmd[cmd.index('-c')]='-E';cmd+=['-CC','-I'+str(ROOT/'tools'),'-DTLK_PRIVATE_COMPILED_HOOKS=1','-DTLK_FORCE_SCENE_PRESENTATION=1']
    with (out/'preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    context=ROOT/'tools/pride_restart_context.c';text=context.read_text();begin=text.index('#define PRIDE_STATE_FIELDS(X)');end=text.index('#define STATE_ENUM',begin)
    fields=re.findall(r'X\((\w+),[^)]+\)',text[begin:end]);assert len(fields)>50
    aliases={'spawn_native_x':'spawn_native[0]','spawn_native_y':'spawn_native[1]','spawn_selected_x':'spawn_selected[0]','spawn_selected_y':'spawn_selected[1]'}
    reset_source=ROOT/'tools/pride_machine_reset_probe.c';cleanup=reset_source.read_text()
    anchor='#define MACHINE_CLEAR(name,limit) name=0;\n    PRIDE_STATE_FIELDS(MACHINE_CLEAR)\n#undef MACHINE_CLEAR';assert cleanup.count(anchor)==1
    cleanup=cleanup.replace(anchor,'\n'.join('    '+aliases.get(name,name)+'=0;' for name in fields));cleanup=re.sub(r'\bNULL\b','((void *)0)',cleanup)
    source=preprocessed.read_text();assert 'PrideOverlayWideDraw' not in source
    for old,new in (
        ('static void DrawToast(void) {','static unsigned long s_sp_toast_calls;\nstatic void DrawToast(void) { ++s_sp_toast_calls;'),
        ('static void Present(void) {','static void Present(void);\nstatic void PresentCore(void) {')):
        assert source.count(old)==1,old;source=source.replace(old,new)
    observer=ROOT/'tools/pride_singlepass_present_probe.c';generated=out/'singlepass.i';generated.write_text(source+'\n'+cleanup+'\n'+observer.read_text())
    obj=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    response=argv('response '+(base/'machine.rsp').read_text())[1:];key=(base/'host.obj').as_posix();assert response.count(key)==1;response[response.index(key)]=obj.as_posix()
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    rsp=out/'singlepass.rsp';rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix();binary=out/'singlepass.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'singlepass.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    backend=base/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    paths=[Path(__file__),base_path,original_host,host_source,context,reset_source,observer,preprocessed,patched,generated,patcher,backend,out/backend.name,*cloned.keys(),*cloned.values(),*sorted(patches.glob('*.hunks'))]
    for name in (out/'preprocess.d').read_text().replace('\\\n',' ').split()[1:]:
        p=Path(name);p=p if p.is_absolute() else cwd/p
        try:p.resolve().relative_to(ROOT)
        except ValueError:continue
        if p.is_file():paths.append(p.resolve())
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=original['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Single-pass mixed player linked',flush=True)


if __name__=='__main__':main()
