"""Qualify private83 flag-transition failure without changing its runtime state."""
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
    priorpath=ROOT/'build/pride-menu-enable85/report.json';prior=bound(priorpath)
    assert prior['result']=='FAIL'
    base=ROOT/'build/pride-menu-output83';bp=base/'build-report.json';b=bound(bp)
    stats=ROOT/'build/pride-menu-output84-isolation';out=ROOT/'build/pride-menu-enable86-observer';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    source=ROOT/'tools/menu_enable_state_probe86.c';cmd=b['compiles']['owner'].copy()
    for flag,value in [('-c',source),('-o',out/'probe.obj'),('-MT',out/'probe.obj'),('-MF',out/'probe.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    inputs=argv('link '+(stats/'link.rsp').read_text())[1:]+[(out/'probe.obj').as_posix(),'-Wl,--wrap=TlkAudioFrame']
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    checks={};commands={};observations={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    for name in ('native','adjustment'):
        folder=out/name;folder.mkdir();run=prior['commands'][name].copy();run[0]=str(out/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(run[run.index(flag)+1]).read_bytes());run[run.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:run[run.index(flag)+1]=str(folder/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_MENU_ENABLE_STATE=str(folder/'flags.csv'),TLK_MENU_OUTPUT_STATS=str(folder/'output.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(run,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        control=priorpath.parent/name
        checks[name+'_all900_guest_neutral']=rc==0 and re.findall(pattern,(folder/'run.log').read_text())==re.findall(pattern,(control/'run.log').read_text())
        checks[name+'_whole_pcm_neutral']=pcm(folder)==pcm(control)
        rows=list(csv.DictReader((folder/'flags.csv').open()));changes=[];last=None
        for row in rows:
            state=int(row['effects'])
            if int(row['field'])>=602 and state!=last:changes.append((int(row['field']),state));last=state
        checks[name+'_off_on_real_flags']=[value for _,value in changes]==[1,0,1]
        observations[name]=dict(changes=changes)
        commands[name]=run
    checks['existing_selected_voice_not_filtered']=prior['observations']['adjustment']['muted_nonzero_samples']==0
    paths=[Path(__file__),priorpath,bp,source,rsp]
    report=dict(result='NEUTRAL_ENABLE_TRANSITION_OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                prior_bad_two_event_expectation_retained=True,explanation='Effects-disabled native wrapper does not reach the logged dispatch when turning effects back on. One Off event is expected; completed flags prove both ordinary changes.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,observations,flush=True)


if __name__=='__main__':main()
