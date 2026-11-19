"""Build isolated default/checkpoint coordinator and presentation audit hosts.

All actual link inputs are pinned; established binaries remain untouched.
"""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    base=ROOT/'build/pride-compiled-revival';out=ROOT/'build/pride-grounded';out.mkdir(exist_ok=True)
    folder=ROOT/'engine/build-win';report_path=base/'build-report.json';original=json.loads(report_path.read_text())
    generation_path=out/'generation-report.json';generation=json.loads(generation_path.read_text())
    for report in (original,generation):
        for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    clones={name+'.obj':out/'objects'/(name+'.obj') for name in generation['instrumented_units']}
    for name,sha in generation['generated_sha256'].items():assert digest(out/'generated'/name)==sha,name
    primary={name:digest(ROOT/name) for name in original['production_sha256']}
    for name,sha in primary.items():assert sha==original['production_sha256'][name],name
    sources=[Path(__file__),report_path,generation_path,ROOT/'tools/pride_grounded_probe.c',
             ROOT/'tools/pride_grounded_prepared_objects.c',ROOT/'tools/pride_prepared_history_api.h',
             ROOT/'tools/pride_grounded_restore.c',ROOT/'tools/pride_grounded_owner.c',ROOT/'tools/pride_grounded_service.h',
             ROOT/'tools/pride_scene_render_bridge.h',ROOT/'tools/pride_scene_prepared_objects.c',
             ROOT/'tools/pride_grounded_render_wide.c',ROOT/'tools/pride_scene_prepare_probe.c',
             ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',
             ROOT/'tools/pride_grounded_compiled_hooks.h',ROOT/'engine/runner/tlk_wide.c',
             ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h',
             ROOT/'engine/runner/tlk_savestate.c',ROOT/'engine/runner/tlk_state_bytes.h']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    ninja='C:/mingw32/bin/ninja.exe';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=folder))
    (out/'objects').mkdir(exist_ok=True)
    import concurrent.futures
    def compile_clone(item):
        name,obj=item;unit=name[:-4]
        suffix='CMakeFiles/snesrecomp_game.dir/generated/snesrecomp/'+name
        entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        command=argv(entry['command'])
        for flag,value in (('-c',(out/'generated'/unit).as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        command+=['-I'+str(ROOT/'tools')]
        cache=obj.with_name(unit+'.cache.json')
        metadata=dict(source=digest(out/'generated'/unit),command=command,compiler=digest(Path(command[0])))
        if cache.exists() and obj.exists():
            prior=json.loads(cache.read_text())
            if all(prior.get(k)==v for k,v in metadata.items()) and prior.get('object')==digest(obj):return
        with (out/'objects'/(unit+'.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        cache.write_text(json.dumps(dict(**metadata,object=digest(obj))))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(compile_clone,clones.items()))
    results={}
    for host in ('probe','sdl'):
        target='tlk_scene_prepared_'+host
        suffix='CMakeFiles/'+target+'.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
        entry=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
        obj=out/('private-'+host+'-host.obj');command=argv(entry['command'])
        for flag,value in (('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        command[command.index('-c')+1]=(ROOT/'tools/pride_grounded_probe.c').as_posix()
        command+=['-I'+str(ROOT/'tools'),'-DTLK_PRIVATE_COMPILED_HOOKS=1','-DTLK_FORCE_SCENE_PRESENTATION=1']
        with (out/(host+'-compile.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        wide_suffix='CMakeFiles/'+target+'.dir/C_/TEMP2/lionKing/tools/pride_scene_prepared_objects.c.obj'
        wide_entry=next(r for r in db if r.get('output','').replace('\\','/')==wide_suffix)
        wide_obj=out/('private-'+host+'-wide.obj');wide_command=argv(wide_entry['command'])
        for flag,value in (('-c',(ROOT/'tools/pride_grounded_prepared_objects.c').as_posix()),('-o',wide_obj.as_posix()),('-MF',wide_obj.as_posix()+'.d'),('-MT',wide_obj.as_posix())):
            wide_command[wide_command.index(flag)+1]=value
        wide_command+=['-I'+str(ROOT/'tools')]
        with (out/(host+'-wide-compile.log')).open('wb') as log:
            subprocess.run(wide_command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        link=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=folder,text=True).splitlines()[-1]
        assert link.count('&&')==2
        command=argv(link.split('&&',1)[1].rsplit('&&',1)[0].strip())
        index=next(n for n,a in enumerate(command) if a.startswith('@'))
        response=argv('response '+(folder/command[index][1:]).read_text())[1:]
        replacements={'CMakeFiles/snesrecomp_game.dir/generated/snesrecomp/'+name:path.as_posix() for name,path in clones.items()}
        replacements[suffix]=obj.as_posix();replacements[wide_suffix]=wide_obj.as_posix();replaced=set()
        for n,arg in enumerate(response):
            key=arg.replace('\\','/')
            if key in replacements:response[n]=replacements[key];replaced.add(key)
        assert replaced==set(replacements)
        # Pin every actual object used, including untouched native renderer and
        # runtime objects. This inventory is stable across subsequent hosts.
        inputs={}
        for arg in response:
            if arg.lower().endswith(('.obj','.a')):
                p=Path(arg);p=p if p.is_absolute() else folder/p
                inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        rsp=out/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response))
        command[index]='@'+rsp.as_posix();binary=out/('grounded-'+host+'.exe')
        command[command.index('-o')+1]=binary.as_posix()
        for n,arg in enumerate(command):
            if arg.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/(host+'.dll.a')).as_posix()
        with (out/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
        results[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
        print('Isolated default revival '+host+' linked',flush=True)
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    for name,sha in primary.items():assert digest(ROOT/name)==sha,name
    (out/'build-report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,runs=results,
        source_sha256=identities,production_sha256=primary,production_behavior_enabled=False,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
