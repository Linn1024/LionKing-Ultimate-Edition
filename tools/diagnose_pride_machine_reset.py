"""Capture the first divergent native field around the real mixed-player reset."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment


def main():
    base=ROOT/'build/pride-machine-player';build_path=base/'build-report.json';build=bound(build_path)
    out=base/'diagnostic';out.mkdir();original=base/'machine.i';source=original.read_text()
    anchor='    return __real_RtlRunFrame(inputs);';assert source.count(anchor)==1
    injected='''    _Bool result=__real_RtlRunFrame(inputs);
    if(snes_frame_counter==39) {
        const char *root=getenv("TLK_SCENE_OWNER_PROBE");char p[4096];
        snprintf(p,sizeof p,"%s/%s-wram.bin",root,machine_injected?"after":"before");
        FILE *f=fopen(p,"wb");if(!f || fwrite(g_ram,1,0x20000,f)!=0x20000)exit(95);fclose(f);
        snprintf(p,sizeof p,"%s/%s-clocks.json",root,machine_injected?"after":"before");
        f=fopen(p,"w");if(!f)exit(95);
        fprintf(f,"{\\"master\\":%llu,\\"port\\":%llu,\\"pending\\":%llu}\\n",
            (unsigned long long)g_cpu.master_cycles,(unsigned long long)g_snes->apu->portClock,(unsigned long long)s_apu_pending_master);fclose(f);
        if(machine_injected || !getenv("TLK_MACHINE_RESET_AT"))exit(0);
    }
    return result;'''
    generated=out/'diagnostic.i';generated.write_text(source.replace(anchor,injected))
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));suffix=f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix);obj=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',generated.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
    subprocess.run(cmd,cwd=cwd,check=True,timeout=120)
    response=argv('response '+(base/'machine.rsp').read_text())[1:];index=response.index((base/'host.obj').as_posix());response[index]=obj.as_posix()
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    rsp=out/'diagnostic.rsp';rsp.write_text(subprocess.list2cmdline(response));index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix();binary=out/'diagnostic.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine'];subprocess.run(cmd,cwd=cwd,check=True,timeout=120)
    import shutil
    backend=base/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    commands={}
    for kind in ('cold','soft','init'):
        folder=out/kind;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',base/'md/resources.ini','--config',config,'--input',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape','--frames',3000,'--speedrun','practice','--no-audio','--no-record','--no-pace']
        env=environment(folder)
        if kind!='cold':env.update(TLK_MACHINE_RESET_AT='2002',TLK_MACHINE_RESET_KIND=kind)
        commands[kind]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[kind],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert not r.returncode,(kind,r.returncode)
        print(kind,'captured39',flush=True)
    a=(out/'cold/before-wram.bin').read_bytes();differences={}
    for kind in ('soft','init'):
        b=(out/kind/'after-wram.bin').read_bytes();differences[kind]=[dict(address=hex(i),cold=x,reset=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    inputs={}
    for item in response:
        if item.lower().endswith(('.obj','.a')):
            p=Path(item);p=p if p.is_absolute() else cwd/p;inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    paths=[Path(__file__),build_path,original,generated,backend]
    report=dict(result='OBSERVED',differences=differences,commands=commands,binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(differences,flush=True)


if __name__=='__main__':main()
