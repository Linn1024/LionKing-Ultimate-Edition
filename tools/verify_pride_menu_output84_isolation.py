"""Actual dry menu voice replacement, each independent source and unchanged guest work."""
import csv
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
    base=ROOT/'build/pride-menu-output83';bp=base/'build-report.json';build=bound(bp)
    origin=ROOT/'build/pride-menu-audio80/route/report.json';prior=bound(origin)
    out=ROOT/'build/pride-menu-output84-isolation';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    source=ROOT/'tools/menu_output_stats84.c';cmd=build['compiles']['owner'].copy()
    for flag,value in [('-c',source),('-o',out/'stats.obj'),('-MT',out/'stats.obj'),('-MF',out/'stats.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:]+[(out/'stats.obj').as_posix(),'-Wl,--wrap=TlkNativeAudioOwnerMute']
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==323 and all(linked[p]==sha for p,sha in build['link_inputs_sha256'].items())
    cases={'native':(None,[],None),'cursor':('title_cursor',[100],592),
           'selection':('title_selection',[101,101],602),'adjustment':('options_adjustment',[101,101],630),
           'exit':('options_exit',[],694)}
    checks={};commands={};observations={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    expected=[row for row in re.findall(pattern,(origin.parent/'native/run.log').read_text()) if int(row[0])<=900]
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    for name,(key,values,first) in cases.items():
        folder=out/name;folder.mkdir();run=prior['commands']['native'].copy();run[0]=str(out/'player.exe');run[run.index('--frames')+1]='900'
        profile=Path(run[run.index('--resource-profile')+1]).read_text()
        if key:profile+='\naudio.effects.'+key+' = md\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(run[run.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:run[run.index(flag)+1]=str(folder/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_MENU_OUTPUT_STATS=str(folder/'output.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_SEMANTIC_OWNER_TRACE=str(folder/'owner.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(run,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        actual=re.findall(pattern,(folder/'run.log').read_text());checks[name+'_all900_native_guest_fields']=rc==0 and actual==expected and len(actual)==900
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        checks[name+'_only_selected_menu_commands']=[(r['selector'],int(r['value'])) for r in driver]==[('2',v) for v in values]
        stats=list(csv.DictReader((folder/'output.csv').open()));muted=sum(int(r['nonzero_muted']) for r in stats)
        checks[name+'_actual_sounding_voice_filter']=(muted>0) if key else not any(int(r['muted']) for r in stats)
        checks[name+'_no_echo_voice_filter']=not any(int(r['echo_muted']) for r in stats)
        if key:
            actual_pcm=pcm(folder);control=pcm(out/'native');acc=0.;samples=0
            for _ in range(first-1):acc+=48000/(21477272/357366);n=int(acc);acc-=n;samples+=n
            checks[name+'_output_identical_before_own_cue']=actual_pcm[:samples*4]==control[:samples*4]
            checks[name+'_own_output_changes']=actual_pcm!=control
        else:
            data=pcm(folder);checks['read_only_wrapper_pcm_neutral']=data==pcm(origin.parent/'native')[:len(data)]
        commands[name]=run;observations[name]=dict(nonzero_muted_samples=muted,commands=driver)
        print(name,'nonzero muted samples',muted,flush=True)
    paths=[Path(__file__),bp,origin,source,rsp]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                binary_sha256=digest(out/'player.exe'),all323_link_inputs_sha256=linked,
                native_queue_spc_and_guest_preserved=True,whole_title_or_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
