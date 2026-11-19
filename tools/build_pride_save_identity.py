"""Build two resource-editor variants sharing an explicit private save identity."""
import copy
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_save_identity import make_contract,contract_identity
from summarize_pride_practice import bound


def main():
    parent=ROOT/'build/pride-legacy-save/player';base_path=parent/'build-report.json';base=bound(base_path)
    closure_path=ROOT/'build/pride-tree-help2/build-report.json';closure=bound(closure_path)
    out=ROOT/'build/pride-save-identity';out.mkdir();source_path=parent/'legacy.i';original=source_path.read_text()
    start=original.index('int main(int argc,char **argv) {');end=original.index('    int result=component_headless_main(argc,argv);',start)
    old=original[start:end];assert 'sha256_compute(bytes,(size_t)size,build_digest)' in old
    inputs=base['runs']['mixed']['link_inputs_sha256'];host_key='build/pride-legacy-save/player/host.obj'
    private={name:sha for name,sha in closure['source_sha256'].items() if name.startswith('tools/') and name.endswith(('.c','.h')) and 'present_probe' not in name}
    assert 'tools/pride_practice_context.c' in private and 'tools/pride_preparation_cache.h' in private
    backend=parent/'genesis_plus_gx_libretro.dll';contract=make_contract(inputs,host_key,private,digest(backend));runs={}
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl';db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    suffix=f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj';row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    paths=[Path(__file__),ROOT/'tools/pride_save_identity.py',base_path,closure_path,source_path,backend]
    for label in ('a','b','incompatible'):
        value=copy.deepcopy(contract)
        if label=='incompatible':value['compatibility_epoch']+=1
        identity=contract_identity(value);manifest=out/(label+'-compatibility.json');manifest.write_text(json.dumps(value,indent=2)+'\n');paths.append(manifest)
        constant='static const unsigned char kPrideSaveCompatibility[32]={'+','.join('0x'+identity[i:i+2] for i in range(0,64,2))+'};\n'
        replacement=constant+'_Static_assert(sizeof(void *)==4,"save compatibility requires reviewed 32-bit ABI");\nint main(int argc,char **argv) {\n    memcpy(build_digest,kPrideSaveCompatibility,32);\n'
        text=original[:start]+replacement+original[end:]
        if label=='b':assert text.count('VERSION RESOURCES')==1;text=text.replace('VERSION RESOURCES','RESOURCE SOURCES')
        generated=out/(label+'.i');generated.write_text(text);paths.append(generated);obj=out/(label+'-host.obj');cmd=argv(row['command'])
        for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        response=argv('response '+(parent/'mixed.rsp').read_text())[1:];key=(parent/'host.obj').as_posix();assert response.count(key)==1;response[response.index(key)]=obj.as_posix()
        raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
        rsp=out/(label+'.rsp');rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix();binary=out/(label+'.exe');cmd[cmd.index('-o')+1]=binary.as_posix()
        for i,arg in enumerate(cmd):
            if arg.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/(label+'.dll.a')).as_posix()
        cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
        with (out/(label+'-link.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        linked={}
        for arg in response:
            if arg.lower().endswith(('.obj','.a')):
                p=Path(arg);p=p if p.is_absolute() else cwd/p;linked[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[label]=dict(binary_sha256=digest(binary),save_compatibility_sha256=identity,link_inputs_sha256=linked)
        print(label,'linked',identity,flush=True)
    shutil.copy2(backend,out/backend.name);paths.append(out/backend.name)
    report=dict(result='BUILT',runs=runs,private_source_count=len(private),
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},production_sha256=base['runs']['mixed']['production_sha256'],
                public_player_enabled=False,legacy_migration_verified=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
