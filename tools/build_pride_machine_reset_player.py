"""Link real machine reset cleanup into the complete private mixed player."""
import json
from pathlib import Path
import re
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-cli-practice';base_path=base/'build-report.json';original=bound(base_path)
    out=ROOT/'build/pride-machine-player';out.mkdir(exist_ok=True)
    assert not (out/'build-report.json').exists(),'Preserve completed builds'
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    context=ROOT/'tools/pride_restart_context.c';text=context.read_text();begin=text.index('#define PRIDE_STATE_FIELDS(X)');end=text.index('#define STATE_ENUM',begin)
    fields=re.findall(r'X\((\w+),[^)]+\)',text[begin:end]);assert len(fields)>50
    aliases={'spawn_native_x':'spawn_native[0]','spawn_native_y':'spawn_native[1]','spawn_selected_x':'spawn_selected[0]','spawn_selected_y':'spawn_selected[1]'}
    probe=ROOT/'tools/pride_machine_reset_probe.c';cleanup=probe.read_text()
    anchor='#define MACHINE_CLEAR(name,limit) name=0;\n    PRIDE_STATE_FIELDS(MACHINE_CLEAR)\n#undef MACHINE_CLEAR'
    assert cleanup.count(anchor)==1
    cleanup=cleanup.replace(anchor,'\n'.join('    '+aliases.get(name,name)+'=0;' for name in fields))
    cleanup=re.sub(r'\bNULL\b','((void *)0)',cleanup)
    host_source=base/'patched/sdl_main.c';host=out/'machine.i';host.write_text(host_source.read_text()+'\n'+cleanup)
    sources=[Path(__file__),base_path,context,probe,host_source,host,ROOT/'tools/pride_machine_reset_wide.c']
    replacements={}
    for name,source,suffix in (
        ('host',host,f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'),
        ('wide',ROOT/'tools/pride_machine_reset_wide.c',f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_prepared_objects.c.obj')):
        row=next(r for r in db if r.get('output','').replace('\\','/')==suffix);obj=out/(name+'.obj');cmd=argv(row['command'])
        for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        cmd+=['-I'+str(ROOT/'tools')]
        with (out/(name+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        replacements[(base/'after.obj').as_posix() if name=='host' else 'C:/TEMP2/lionKing/build/pride-overlay/private-sdl-wide.obj']=obj.as_posix()
    response=argv('response '+(base/'after.rsp').read_text())[1:];found=set()
    for i,a in enumerate(response):
        key=a.replace('\\','/')
        if key in replacements:response[i]=replacements[key];found.add(key)
    assert found==set(replacements),(found,set(replacements))
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(i for i,a in enumerate(cmd) if a.startswith('@'))
    rsp=out/'machine.rsp';rsp.write_text(subprocess.list2cmdline(response));cmd[index]='@'+rsp.as_posix();binary=out/'machine.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'machine.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs={}
    for a in response:
        if a.lower().endswith(('.obj','.a')):
            p=Path(a);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    backend=base/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name);sources.extend((backend,out/backend.name))
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},production_sha256=original['production_sha256'],
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Mixed machine reset player linked',flush=True)


if __name__=='__main__':main()
