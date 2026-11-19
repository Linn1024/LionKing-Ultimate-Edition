"""Stage accurate loader errors without changing linked emulation core objects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    parent=ROOT/'build/pride-tree-help2';out=ROOT/'build/pride-legacy-save/player';out.mkdir(parents=True)
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    patches=ROOT/'engine/cmake/game-patches';patcher=ROOT/'engine/scripts/apply_runtime_patches.py'
    subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',ROOT/'engine','--out',out/'game'],check=True,timeout=60)
    guard=ROOT/'tools/pride_legacy_save_guard.c';host=parent/'singlepass.i';text=host.read_text()
    anchor='static int PrideStateLoad(const char *path,uint32_t *field) {';assert text.count(anchor)==1
    text=text.replace(anchor,guard.read_text()+'\n'+anchor)
    anchor='    int ok=size>STATE_BYTES && !memcmp(record,"PRHSAVE1",8)';assert text.count(anchor)==1
    text=text.replace(anchor,'    if(PrideLegacyNativeSave(record,size)) { free(record);pride_error_ui_log(attempt_field,0,0);return 0; }\n'+anchor)
    generated=out/'legacy.i';generated.write_text(text);runs={};paths=[Path(__file__),patcher,guard,host,generated,*sorted(patches.glob('*.hunks'))]
    for name,target,folder,response_file in (('mixed','tlk_scene_prepared_sdl',parent,'singlepass.rsp'),('native','tlk_sdl',parent/'plain-native','native.rsp')):
        base_path=folder/'build-report.json';base=bound(base_path);paths.append(base_path)
        for file,sha in base['link_inputs_sha256'].items():assert digest(ROOT/file)==sha,file
        response=argv('response '+(folder/response_file).read_text())[1:];replacements={}
        suffix=f'CMakeFiles/{target}.dir/runner/tlk_savestate.c.obj'
        row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        obj=out/(name+'-state.obj');cmd=argv(row['command'])
        for flag,value in (('-c',(out/'game/tlk_savestate.c').as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        with (out/(name+'-state-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        replacements[suffix]=obj.as_posix()
        if name=='mixed':
            suffix_host='CMakeFiles/tlk_scene_prepared_sdl.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
            row=next(r for r in db if r.get('output','').replace('\\','/')==suffix_host);obj=out/'host.obj';cmd=argv(row['command'])
            for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
            with (out/'host-compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            replacements[(parent/'host.obj').as_posix()]=obj.as_posix()
        for key,value in replacements.items():assert response.count(key)==1;response[response.index(key)]=value
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
        if '&&' in cmd:cmd=cmd[:cmd.index('&&')]
        rsp=out/(name+'.rsp');rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix()
        binary=out/(name+'.exe');cmd[cmd.index('-o')+1]=binary.as_posix()
        for i,a in enumerate(cmd):
            if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/(name+'.dll.a')).as_posix()
        if name=='mixed':cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
        with (out/(name+'-link.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        inputs={}
        for arg in response:
            if arg.lower().endswith(('.obj','.a')):
                p=Path(arg);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[name]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs,production_sha256=base['production_sha256'])
        print(name,'legacy handling linked',flush=True)
    backend=parent/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name);paths.extend([backend,out/backend.name,*sorted((out/'game').glob('*.c'))])
    report=dict(result='BUILT',runs=runs,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
