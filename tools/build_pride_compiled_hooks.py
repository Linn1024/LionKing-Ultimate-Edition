"""Build an isolated instrumented private executable from Ninja's real commands.

Reuses untouched production objects; only selected generated clones and the
private hook host are rebuilt. No production generated source/object/executable
or framework source is overwritten. Requires the retained private link rsp.
"""
import concurrent.futures
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def argv(command):
    count=C.c_int();shell=C.WinDLL('shell32');kernel=C.WinDLL('kernel32')
    shell.CommandLineToArgvW.argtypes=[C.c_wchar_p,C.POINTER(C.c_int)]
    shell.CommandLineToArgvW.restype=C.POINTER(C.c_wchar_p)
    kernel.LocalFree.argtypes=[C.c_void_p]
    pointer=shell.CommandLineToArgvW(command,C.byref(count))
    if not pointer:raise OSError('CommandLineToArgvW failed')
    try:return [pointer[n] for n in range(count.value)]
    finally:kernel.LocalFree(C.cast(pointer,C.c_void_p))


def main():
    out=ROOT/'build/pride-compiled-revival';objects=out/'objects';objects.mkdir(exist_ok=True)
    generated=out/'generated';manifest_path=out/'generation-report.json'
    manifest=json.loads(manifest_path.read_text());assert manifest['result']=='GENERATED'
    for name,sha in manifest['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in manifest['generated_sha256'].items():assert digest(generated/name)==sha,name
    folder=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    primary=[folder/'tlk_sdl.exe',folder/'tlk_headless.exe',ROOT/'dist/LionKing.exe']
    before={str(p):digest(p) for p in primary}
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=folder))
    tasks=[];replacements={}
    for name in manifest['instrumented_units']:
        suffix='CMakeFiles/snesrecomp_game.dir/generated/snesrecomp/'+name+'.obj'
        entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        target=objects/(name+'.obj');tasks.append((name,entry,generated/name,target,False));replacements[suffix]=target.as_posix()
    suffix='CMakeFiles/tlk_scene_restore_probe.dir/C_/TEMP2/lionKing/tools/pride_scene_restore_probe.c.obj'
    entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    target=objects/'private-host.obj';tasks.append(('private-host',entry,ROOT/'tools/pride_scene_restore_probe.c',target,True))
    replacements[suffix]=target.as_posix()
    sources={manifest_path,ROOT/'tools/pride_scene_compiled_hooks.h',ROOT/'tools/pride_scene_compiled_hooks_api.h',
             ROOT/'tools/pride_scene_restore_probe.c',Path(__file__)}
    def compile_one(task):
        name,entry,source,target,host=task
        command=argv(entry['command'])
        assert command and 'cmd.exe' not in command[0].lower()
        for flag,value in (('-c',source.as_posix()),('-o',target.as_posix()),('-MF',target.as_posix()+'.d'),('-MT',target.as_posix())):
            position=command.index(flag);command[position+1]=value
        command+=['-I'+str(ROOT/'tools')]
        if host:command+=['-DTLK_PRIVATE_COMPILED_HOOKS=1']
        with (objects/(name+'.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        return name,entry,source,target
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for name,entry,source,target in pool.map(compile_one,tasks):
            sources.add(source);print('Compiled isolated '+name,flush=True)
    link=subprocess.check_output([ninja,'-t','commands','tlk_scene_restore_probe.exe'],cwd=folder,text=True).splitlines()[-1]
    assert link.count('&&')==2
    command=argv(link.split('&&',1)[1].rsplit('&&',1)[0].strip())
    rsp_index=next(n for n,arg in enumerate(command) if arg.startswith('@'))
    old_rsp=folder/command[rsp_index][1:]
    response=argv('response '+old_rsp.read_text())[1:]
    replaced=set()
    for n,arg in enumerate(response):
        key=arg.replace('\\','/')
        if key in replacements:response[n]=replacements[key];replaced.add(key)
    assert replaced==set(replacements),(set(replacements)-replaced)
    private_rsp=out/'compiled-restore.rsp'
    private_rsp.write_text(subprocess.list2cmdline(response))
    command[rsp_index]='@'+private_rsp.as_posix()
    binary=out/'compiled-restore.exe';command[command.index('-o')+1]=binary.as_posix()
    for n,arg in enumerate(command):
        if arg.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/'compiled-restore.dll.a').as_posix()
    with (out/'link.log').open('wb') as log:
        subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for path,sha in before.items():assert digest(Path(path))==sha,path
    report=dict(result='BUILT',scope=__doc__,binary_sha256=digest(binary),
        primary_binaries_unchanged=True,generated_units=len(manifest['instrumented_units']),
        sources_recompiled=len(tasks),compiled_ownership_verified=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        object_sha256={p.name:digest(p) for p in objects.glob('*.obj')},
        production_sha256={str(Path(p).relative_to(ROOT)).replace('\\','/'):sha for p,sha in before.items()})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Isolated private compiled executable linked; primary binaries unchanged',flush=True)


if __name__=='__main__':main()
