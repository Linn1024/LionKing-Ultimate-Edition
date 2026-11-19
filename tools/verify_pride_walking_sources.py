"""Verify native and MD cue selection in the ordinary walking-roar situation."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-walking-response'
    qualification=parent/'qualification/report.json';assert bound(qualification)['result']=='PASS'
    source=parent/'report.json';prior=bound(source)
    out=ROOT/'build/pride-walking-source-comparison';out.mkdir()
    commands={};checks={};folders={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();folders[mode]=folder;cmd=prior['commands']['observer'].copy()
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        profile=folder/'resources.ini';text=profile.read_text();assert text.count('porcupine_attack = md')==1
        profile.write_text(text.replace('porcupine_attack = md','porcupine_attack = snes'))
        if mode=='lle':cmd.append('--lle')
        commands[mode]=cmd
        env=dict(clean,TLK_WALK_ACTOR_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[mode+'_exit']=rc==0;print(mode,rc,flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['all139_native_response_fields']=len(rows(folders['aot']))==139 and rows(folders['aot'])==rows(folders['lle'])
    for name in ('window.png','scene.json','audio.wav','actors.csv','events.csv','tree.jsonl'):
        checks['native_modes_'+name]=digest(folders['aot']/name)==digest(folders['lle']/name)
    actors=list(csv.DictReader((folders['aot']/'actors.csv').open()))
    events=[r for r in csv.DictReader((folders['aot']/'events.csv').open()) if r['event']=='0015' and int(r['frame'])>=3958]
    for actor,timer in [('b593','27'),('ba93','28')]:
        entry=next(r for r in actors if r['actor']==actor and r['field']=='3960')
        checks[actor+'_same_original_entry']=entry['action']=='c15b87' and entry['timer']==timer
        cue=[r for r in events if r['actor']==actor]
        checks[actor+'_native_cue_once']=len(cue)==1
        post=next((r for r in actors if cue and r['actor']==actor and int(r['field'])==int(cue[0]['frame'])+1),None)
        checks[actor+'_native_cue_at_original_timer20']=bool(post) and post['timer']=='19' and post['action']=='c15b87'
    md_events=[r for r in csv.DictReader((parent/'observer/events.csv').open()) if r['event']=='0015' and int(r['frame'])>=3958]
    checks['md_walking_no_cue_and_returning_actor_cues']= [(r['actor'],r['frame']) for r in md_events]==[('ba93','3960')]
    checks['roar_source_remains_md']=all('gameplay.simba.roar = md' in (p/'resources.ini').read_text() for p in folders.values())
    paths=[Path(__file__),qualification,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                native_cue_events=events,md_cue_events=md_events,ordinary_poweron_route=True,
                native_sound_source_preserved=True,only_attack_behavior_choice_changed=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[(r['actor'],r['frame']) for r in events],flush=True)


if __name__=='__main__':main()
