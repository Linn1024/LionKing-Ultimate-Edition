"""Real Off/On flags, request-owned filtering, guest neutrality and current resume."""
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
    base=ROOT/'build/pride-menu-enable86';bp=base/'build-report.json';build=bound(bp)
    oldpath=ROOT/'build/pride-menu-enable85/report.json';old=bound(oldpath)
    mdpath=ROOT/'build/pride-menu-enable85-md2/report.json';md=bound(mdpath)
    observation=ROOT/'build/pride-menu-enable86-observer/report.json';obs=bound(observation)
    assert md['result']=='ORIGINAL_EFFECTS_ENABLE_CAPTURED' and obs['result']=='NEUTRAL_ENABLE_TRANSITION_OBSERVED'
    out=base/'enable';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    stats=ROOT/'build/pride-menu-output84-isolation/stats.obj';probe=ROOT/'build/pride-menu-enable86-observer/probe.obj'
    inputs=argv('link '+(base/'link.rsp').read_text())[1:]+[stats.as_posix(),probe.as_posix(),'-Wl,--wrap=TlkNativeAudioOwnerMute,--wrap=TlkAudioFrame']
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    checks={};commands={};observations={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    def run(name,mode='aot',load=False):
        folder=out/name;folder.mkdir();selected=name!='native';cmd=old['commands']['adjustment' if selected else 'native'].copy();cmd[0]=str(out/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name=='adjustment-aot':cmd+=['--save-at','683',str(folder/'current.state')]
        if mode=='lle':cmd+=['--lle']
        if load:
            author=out/'adjustment-aot';row=next(json.loads(line) for line in (author/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==683)
            origin=commands['adjustment-aot'];tape=Path(origin[origin.index('--input-polled')+1]);remaining=folder/'remaining.polled.tape'
            remaining.write_bytes(tape.read_bytes()[row['poll_index']*2:]);cmd[cmd.index('--input-polled')+1]=str(remaining)
            cmd+=['--load',str(author/'current.state')]
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_MENU_ENABLE_STATE=str(folder/'flags.csv'),TLK_MENU_OUTPUT_STATS=str(folder/'output.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;commands[name]=cmd;print(name,rc,flush=True);return folder
    native=run('native');a=run('adjustment-aot');b=run('adjustment-lle','lle')
    expected=hashes(oldpath.parent/'native')
    for name,folder in [('native',native),('adjustment-aot',a),('adjustment-lle',b)]:
        checks[name+'_all900_guest_fields_native']=len(hashes(folder))==900 and hashes(folder)==expected
        rows=list(csv.DictReader((folder/'flags.csv').open()));changes=[];last=None
        for row in rows:
            if int(row['field'])>=602 and int(row['effects'])!=last:changes.append((int(row['field']),int(row['effects'])));last=int(row['effects'])
        checks[name+'_exact_off_on_flags']=changes==[(602,1),(682,0),(710,1)]
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        checks[name+'_correct_single_off_cue']=[(r['selector'],r['value']) for r in driver]==([] if name=='native' else [('2','101')])
        stats_rows=list(csv.DictReader((folder/'output.csv').open()))
        muted_off=sum(int(r['nonzero_muted']) for r in stats_rows if 682<=int(r['field'])<710)
        checks[name+'_accepted_voice_muted_while_effects_off']=(muted_off>0) if name!='native' else muted_off==0
        observations[name]=dict(flags=changes,nonzero_muted_during_off=muted_off,driver=driver)
    checks['native_whole_pcm_preserved']=pcm(native)==pcm(oldpath.parent/'native')
    checks['selected_whole_pcm_mode_parity']=pcm(a)==pcm(b)
    checks['old83_duplicate_replaced']=pcm(a)!=pcm(oldpath.parent/'adjustment')
    for field,file in [('scene','scene.json'),('window','window.png')]:checks[field+'_mode_parity']=digest(a/file)==digest(b/file)
    identity=digest(a/'current.state')
    for mode in ('aot','lle'):
        name='resume-'+mode;folder=run(name,mode,True)
        checks[name+'_remaining217_guest_exact']=len(hashes(folder))==217 and hashes(folder)==[r for r in hashes(a) if int(r[0])>683]
        tail=pcm(folder);checks[name+'_playing_pcm_suffix_exact']=bool(tail) and pcm(a)[-len(tail):]==tail
        for file in ('scene.json','window.png'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(a/file)
    checks['current_state_unchanged']=digest(a/'current.state')==identity
    paths=[Path(__file__),bp,oldpath,mdpath,observation,stats,probe,rsp]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                current_build_only=True,guest_or_original_queue_edits=False,full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
