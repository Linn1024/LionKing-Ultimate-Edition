"""Qualify an ordinary walking response, cue attribution and real cold saves."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm


def main():
    out=ROOT/'build/pride-walking-response';out.mkdir()
    source=ROOT/'build/pride-walking-recharge/report.json';research=bound(source)
    original_source=ROOT/'build/pride-porcupine-walk-contract/report.json';original=bound(original_source)
    assert original['result']=='PASS' and all(research['checks'].values())
    first=ROOT/'build/pride-walking-inputs/seed-observer'
    ledge=source.parent/'ledge-seed'
    native_tape=ROOT/'build/pride-porcupine-walk-calls-search/neutral.poweron.tape'
    prefix_count=json.loads((first/'tree.jsonl').read_text().splitlines()[-1])['poll_index']
    ledge_count=json.loads((ledge/'tree.jsonl').read_text().splitlines()[-1])['poll_index']
    approach_tape=Path(research['commands']['ledge-seed'][research['commands']['ledge-seed'].index('--input-polled')+1])
    tail=Path(research['commands']['up32'][research['commands']['up32'].index('--input-polled')+1])
    tape=out/'ordinary.poweron.tape'
    tape.write_bytes(native_tape.read_bytes()[:prefix_count*2]+approach_tape.read_bytes()[:ledge_count*2]+tail.read_bytes())
    template=research['commands']['up32'].copy()
    i=template.index('--load');del template[i:i+2]
    production=ROOT/'build/pride-sprite-fresh44/player.exe'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    commands={};checks={}
    def run(label,frames=4088,observe=False,lle=False,save=None,load=None,input_tape=tape,debugger=None,attack='md'):
        folder=out/label;folder.mkdir();cmd=template.copy()
        if not observe:cmd[0]=str(production)
        for flag,value in [('--frames',frames),('--input-polled',input_tape),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if attack=='snes':
            p=folder/'resources.ini';text=p.read_text();assert text.count('porcupine_attack = md')==1
            p.write_text(text.replace('porcupine_attack = md','porcupine_attack = snes'))
        if lle:cmd.append('--lle')
        if save:cmd+=['--save-at',str(save),str(folder/'saved.state')]
        if load:cmd+=['--load',str(load)]
        cmd+=['--hash-at',','.join(map(str,range(3950,frames+1)))]
        if debugger:cmd=['C:/mingw32/bin/gdb.exe','--batch','-x',str(debugger),'--args',*cmd]
        commands[label]=cmd
        env=dict(clean,TLK_WALK_ACTOR_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0;print(label,rc,flush=True);return folder
    control=run('production',save=3960)
    warm=run('observer',observe=True)
    lle=run('observer-lle',observe=True,lle=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    samples=lambda p:re.findall(pattern,(p/'run.log').read_text())
    for label,left,right in [('observer_neutral',control,warm),('modes',warm,lle)]:
        checks[label+'_all139_response_fields']=len(samples(left))==139 and samples(left)==samples(right)
        for name in ('window.png','scene.json','audio.wav','events.csv','attack.csv','tree.jsonl'):
            checks[label+'_'+name]=digest(left/name)==digest(right/name)
    actor_rows=list(csv.DictReader((warm/'actors.csv').open()))
    at=lambda field,actor:next(r for r in actor_rows if r['field']==str(field) and r['actor']==actor)
    before=at(3959,'b593');entry=at(3960,'b593')
    checks['walking_before_real_roar']=before['action']=='c150d7' and before['strength']=='0'
    checks['original_walking_poststate']=all(entry[k]==v for k,v in dict(action='c15b87',animation='c28959',timer='27',wait='0',persistent='1',strength='24').items())
    checks['full_poweron_reproduces_cold_search_entry']=entry==research['cases']['up32']['walking_entries'][0]['after']
    countdown=[int(r['timer']) for r in actor_rows if r['actor']=='b593' and r['action']=='c15b87' and 3960<=int(r['field'])<=3987]
    checks['all28_walking_timers']=countdown==list(range(27,-1,-1))
    trace=list(csv.DictReader((warm/'attack.csv').open()))
    target=[r for r in trace if r['actor']=='b593']
    cues=lambda rows:[r for r in rows if r['pc']=='c15cb2' and r['phase_before']=='3']
    checks['walking_attack_starts27']=bool(target) and target[0]['timer']=='27'
    checks['walking_actor_no_timer28_cue']=not cues(target)
    checks['simultaneous_other_actor_retains_idle_cue']=any(r['actor']=='ba93' and r['timer']=='28' for r in cues(trace))
    seed=run('before-entry',frames=3959,save=3959)
    for label,parent,frame in [('pre',seed,3959),('post',control,3960)]:
        row=json.loads((parent/'tree.jsonl').read_text().splitlines()[-1]) if frame==3959 else next(
            json.loads(x) for x in (parent/'tree.jsonl').read_text().splitlines() if json.loads(x)['field']==frame)
        suffix=out/(label+'.suffix.tape');suffix.write_bytes(tape.read_bytes()[row['poll_index']*2:])
        state=parent/'saved.state';identity=digest(state)
        a=run(label+'-cold',load=state,input_tape=suffix)
        b=run(label+'-cold-lle',load=state,input_tape=suffix,lle=True)
        expected=[r for r in samples(control) if int(r[0])>frame]
        checks[label+'_cold_all_fields']=samples(a)==samples(b)==expected
        for name in ('window.png','scene.json','audio.wav','events.csv','attack.csv'):
            checks[label+'_cold_modes_'+name]=digest(a/name)==digest(b/name)
        checks[label+'_cold_picture']=digest(a/'window.png')==digest(control/'window.png')
        tail_pcm=pcm(a/'audio.wav');checks[label+'_remaining_pcm']=bool(tail_pcm) and tail_pcm==pcm(control/'audio.wav')[-len(tail_pcm):]
        checks[label+'_saved_bytes_preserved']=digest(state)==identity
    # The previously qualified debugger reads only guest context. Restrict output
    # to the response interval, leaving the same exact executed code path.
    guest_source=ROOT/'build/pride-walking-guest-context2/report.json';bound(guest_source)
    script=out/'guest-context.gdb';text=(guest_source.parent/'observe.gdb').read_text()
    text=text.replace('silent\n','silent\nif *(unsigned int*)&snes_frame_counter>=3958\n').replace('continue\nend','end\ncontinue\nend')
    script.write_text(text)
    debug=run('guest-context',debugger=script)
    log=(debug/'run.log').read_text()
    checks['guest_walking_helper_at_activation']=bool(re.search(r'HELPER field=3959 actor=b593 action=c150d7 strength=24 .*ret=c151ad',log))
    checks['guest_constructor_from_walking_action']='CONSTRUCTOR field=3959 actor=b593 action=c150d7 strength=24' in log
    checks['debugger_response_fields_neutral']=samples(debug)==samples(control)
    for name in ('window.png','scene.json','audio.wav','events.csv','attack.csv'):
        checks['debugger_'+name+'_neutral']=digest(debug/name)==digest(control/name)
    paths=[Path(__file__),source,original_source,guest_source,tape,production]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                walking_before=before,walking_entry=entry,walking_timers=countdown,
                ordinary_poweron_controller_route=True,guest_or_rom_edits=False,
                no_global_silence_claim=True,renderer_or_runtime_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
