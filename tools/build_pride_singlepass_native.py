"""Build the ordinary native frontend with the same source overlay patch."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-reset/fixed4';base_path=base/'build-report.json';original=bound(base_path)
    parent=ROOT/'build/pride-singlepass';parent_path=parent/'build-report.json';bound(parent_path)
    out=parent/'plain-native';out.mkdir();patched=parent/'patched/sdl_main.c';observer=ROOT/'tools/pride_singlepass_present_probe.c';source=patched.read_text()
    for old,new in (('static void DrawToast(void) {','static unsigned long s_sp_toast_calls;\nstatic void DrawToast(void) { ++s_sp_toast_calls;'),('static void Present(void) {','static void Present(void);\nstatic void PresentCore(void) {')):
        assert source.count(old)==1,old;source=source.replace(old,new)
    generated=out/'native.c';generated.write_text(source+'\n'+observer.read_text())
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));suffix='CMakeFiles/tlk_sdl.dir/runner/sdl_main.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix);obj=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    response=argv('response '+(base/'sdl.rsp').read_text())[1:];assert response.count(suffix)==1;response[response.index(suffix)]=obj.as_posix()
    raw=subprocess.check_output([ninja,'-t','commands','tlk_sdl.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    if '&&' in cmd:cmd=cmd[:cmd.index('&&')]
    rsp=out/'native.rsp';rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix();binary=out/'native.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'native.dll.a').as_posix()
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    backend=parent/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    paths=[Path(__file__),base_path,parent_path,patched,observer,generated,backend,out/backend.name]
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=original['production_sha256'],public_player_enabled=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native one-pass frontend linked',flush=True)


if __name__=='__main__':main()
