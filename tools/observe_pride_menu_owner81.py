"""Read-only original queue/SPC title-effect trace; qualify against private80 PCM."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-audio80';bp=base/'build-report.json';prior=bound(bp)
    route=base/'route/report.json';r=bound(route)
    owner_report=ROOT/'build/pride-music-output65/build-report.json';owner=bound(owner_report)
    original=ROOT/'engine/runner/tlk_native_audio_owner.c';text=original.read_text()
    out=ROOT/'build/pride-menu-owner81';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    def replace(anchor,extra):
        nonlocal text
        assert text.count(anchor)==1,anchor
        text=text.replace(anchor,anchor+extra)
    replace('static void SemAccepted(CpuState *cpu,uint32_t pc) {',
            '\n    if(SemAddress(0xdf)==0xc005ab)SemTrace("title_queue",cpu->X,SemWord(g_ram,0x1f15),SemStackAddress(cpu->S+17)+1);')
    replace('    unsigned token=atomic_exchange(&s_sem_queue[cpu->X],0);',
            '\n    if(SemAddress(0xdf)==0xc005ab)SemTrace("title_transfer",cpu->X,SemWord(g_ram,0x1f6f+cpu->X),cpu->Y);')
    replace('        if(y<64) {',
            '\n            if(SemAddress(0xdf)==0xc005ab)SemTrace("title_dispatch",y,ram[8],ram[0x205+y]);')
    replace('            unsigned stream=SemWord(ram,0x294);',
            '\n            if(SemAddress(0xdf)==0xc005ab && stream>=15)SemTrace("title_software",ram[stream-13],x,ram[stream-12]);')
    replace('        s_music_candidate[x]=a<22?ram[0x2e3+a]:0x100;',
            '\n        if(SemAddress(0xdf)==0xc005ab)SemTrace("title_assigned",s_music_candidate[x],x,a);')
    replace('        s_music_voice[ch]=s_music_latched[ch];',
            '\n        if(SemAddress(0xdf)==0xc005ab)SemTrace("title_keyon",s_music_voice[ch],ch,s_sem_voice[ch]);')
    source=out/'owner.c';source.write_text(text);cmd=owner['compiles']['owner'].copy()
    for flag,value in [('-c',source),('-o',out/'owner.obj'),('-MT',out/'owner.obj'),('-MF',out/'owner.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:];old=owner_report.parent/'owner.obj'
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
    inputs[indices[0]]=(out/'owner.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==322 and sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
    checks={};commands={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for name in ('native','menus-aot'):
        folder=out/name;folder.mkdir();run=r['commands'][name].copy();run[0]=str(out/'player.exe');run[run.index('--frames')+1]='900'
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(run[run.index(flag)+1]).read_bytes());run[run.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:run[run.index(flag)+1]=str(folder/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_SEMANTIC_OWNER_TRACE=str(folder/'owner.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(run,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(base/'route'/name/'run.log').read_text())
        checks[name+'_all900_guest_fields_neutral']=rc==0 and len(actual)==900 and actual==[row for row in expected if int(row[0])<=900]
        with wave.open(str(folder/'audio.wav'),'rb') as sample,wave.open(str(base/'route'/name/'audio.wav'),'rb') as control:
            checks[name+'_whole_pcm_neutral']=sample.readframes(sample.getnframes())==control.readframes(sample.getnframes())
        commands[name]=run;print(name,checks,flush=True)
    paths=[Path(__file__),bp,route,owner_report,original,source,rsp]
    report=dict(result='NEUTRAL_MENU_OWNER_OBSERVER' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,read_only_guest_observation=True,
                owner_algorithm_unchanged=True,menu_output_filter_implemented=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
