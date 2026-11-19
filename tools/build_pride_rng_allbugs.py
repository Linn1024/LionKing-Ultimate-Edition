"""Build an observational tracked-RAM host around the unchanged RNG player2 core."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from summarize_pride_practice import bound


OBSERVER = r'''
static unsigned PrideObservedWord(unsigned at) {
    return g_ram[at] | g_ram[at+1]<<8;
}
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    _Bool result=PrideObservedRunFrame(inputs);
    const char *path=getenv("TLK_TRACKED_RAM_LOG");
    if(path) {
        static FILE *log;
        if(!log) { log=fopen(path,"w");if(!log)exit(96); }
        const uint8_t *r=g_ram;
        fprintf(log,"%u %d %06X %04X %04X %04X %04X %04X %04X\n",
            (unsigned)snes_frame_counter,s_polls_frame==0?1:0,
            (unsigned)(r[0x1e00]|r[0x1e01]<<8|r[0x1e02]<<16),
            PrideObservedWord(0x2004),PrideObservedWord(0xb21b),PrideObservedWord(0xb21d),
            PrideObservedWord(0x1ff9e),PrideObservedWord(0x1ffaa),PrideObservedWord(0x5a));
    }
    return result;
}
'''


def main():
    parent=ROOT/'build/pride-rng-player2'
    bp=parent/'build-report.json';build=bound(bp)
    out=parent/'allbugs-observer';out.mkdir(exist_ok=True)
    assert not (out/'build-report.json').exists()
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    original=parent/'host.i';text=original.read_text()
    anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {'
    assert text.count(anchor)==1
    text=text.replace(anchor,'static _Bool PrideObservedRunFrame(uint32 inputs) {')+'\n'+OBSERVER
    source=out/'host.i';source.write_text(text)
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    target='tlk_scene_prepared_sdl'
    row=next(r for r in db if r.get('output','').replace('\\','/')==f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj')
    host=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',host.as_posix()),('-MF',host.as_posix()+'.d'),('-MT',host.as_posix())):
        cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:
        subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    response=argv('response '+(parent/'player.rsp').read_text())[1:]
    old_host=parent/'host.obj';assert response.count(old_host.as_posix())==1
    response[response.index(old_host.as_posix())]=host.as_posix()
    rsp=out/'player.rsp';rsp.write_text(subprocess.list2cmdline(response))
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    at=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[at]='@'+rsp.as_posix()
    binary=out/'player.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'player.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:
        subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=dict(build['link_inputs_sha256'])
    assert inputs.pop(old_host.relative_to(ROOT).as_posix())==digest(old_host)
    for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
    inputs[host.relative_to(ROOT).as_posix()]=digest(host)
    backend=parent/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    paths=[Path(__file__),bp,original,source,backend,out/backend.name,parent/'save-compatibility.json']
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        all_nonhost_link_inputs_identical=True,guest_writes_added=False,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Read-only All Bugs observer built',flush=True)


if __name__=='__main__':main()
