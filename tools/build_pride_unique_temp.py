"""Keep the save contract/core while giving private temporary files distinct names."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    parent=ROOT/'build/pride-rng-player2';bp=parent/'build-report.json';base=bound(bp)
    out=ROOT/'build/pride-rng-player3';out.mkdir()
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    original=parent/'host.i';text=original.read_text()
    old='''static int temp_path(char *out,size_t capacity,const char *path,const char *suffix) {
    int n=snprintf(out,capacity,"%s%s",path,suffix);return n>0 && (size_t)n<capacity;
}'''
    assert text.count(old)==1
    text=text.replace(old,'''extern int TlkTemporaryPath(char *,size_t,const char *,const char *);
static int temp_path(char *out,size_t capacity,const char *path,const char *suffix) {
    return TlkTemporaryPath(out,capacity,path,suffix);
}''')
    source=out/'host.i';source.write_text(text)
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    row=next(r for r in db if r.get('output','').replace('\\','/')==f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj')
    host=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',host.as_posix()),('-MF',host.as_posix()+'.d'),('-MT',host.as_posix())):cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    helper_source=ROOT/'engine/runner/tlk_temp_path.c';helper=out/'temp-path.obj'
    helper_command=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',str(helper_source),'-o',str(helper)]
    with (out/'helper-compile.log').open('wb') as log:subprocess.run(helper_command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    response=argv('response '+(parent/'player.rsp').read_text())[1:];old_host=parent/'host.obj'
    assert response.count(old_host.as_posix())==1
    response[response.index(old_host.as_posix())]=host.as_posix();response.insert(0,helper.as_posix())
    rsp=out/'player.rsp';rsp.write_text(subprocess.list2cmdline(response))
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    at=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[at]='@'+rsp.as_posix()
    binary=out/'player.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'player.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=dict(base['link_inputs_sha256']);assert inputs.pop(old_host.relative_to(ROOT).as_posix())==digest(old_host)
    for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
    inputs[host.relative_to(ROOT).as_posix()]=digest(host);inputs[helper.relative_to(ROOT).as_posix()]=digest(helper)
    backend=parent/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    contract=parent/'save-compatibility.json';shutil.copy2(contract,out/contract.name)
    paths=[Path(__file__),bp,original,source,helper_source,helper_source.with_suffix('.h'),backend,out/backend.name,contract]
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        production_sha256=base['production_sha256'],save_compatibility_unchanged=True,
        same_existing_nonhost_link_inputs=True,added_host_io_helper=True,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Candidate3 built; existing core and save compatibility retained',flush=True)


if __name__=='__main__':main()
