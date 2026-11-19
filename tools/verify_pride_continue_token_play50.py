"""Exercise natural Sun pickup, independent timing/voice and current-build resume."""
from concurrent.futures import ThreadPoolExecutor
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
    base=ROOT/'build/pride-continue-token-behavior50';build_path=base/'build-report.json';bound(build_path)
    approach_path=base/'pickup-approach/report.json';approach=bound(approach_path);assert approach['result']=='PASS'
    out=base/'pickup-play';out.mkdir();template=approach['commands']['fresh-seed'].copy()
    i=template.index('--save-at');del template[i:i+3]
    tape=out/'pickup.polled.tape';tape.write_bytes(Path(approach['original_tape']).read_bytes()[:approach['prefix_poll_count']*2]+(ROOT/approach['selected']['tail_tape']).read_bytes())
    template[template.index('--input-polled')+1]=str(tape)
    commands={};checks={};clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    definitions=[('native','snes','snes',False,False),('voice','md','snes',False,False),('timing','snes','md',False,False),('both','md','md',False,False),('both-lle','md','md',True,False),('voice-native-music','md','snes',False,True)]
    def run(item):
        label,voice,timing,lle,native_music=item;folder=out/label;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]='2800'
        profile=Path(template[template.index('--resource-profile')+1]).read_text()
        if native_music:profile+='\naudio.music.pride_lands = snes\n'
        profile+='\naudio.effects.world.continue_token = '+voice+'\ngameplay.levels.pride_lands.continue_token_animation = '+timing+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(template[template.index('--config')+1]).read_bytes())
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        cmd+=['--hash-at',','.join(map(str,range(1,2801)))]
        if lle:cmd.append('--lle')
        if label=='both':cmd+=['--save-at','2510',str(folder/'active.state')]
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_CONTINUE_TOKEN_TIMING_TRACE=str(folder/'timing.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label,rc,flush=True);return label,folder,rc
    with ThreadPoolExecutor(max_workers=3) as pool:results={label:(folder,rc) for label,folder,rc in pool.map(run,definitions)}
    def events(folder):
        rows=[]
        for row in csv.DictReader((folder/'events.csv').open()):
            raw=bytes.fromhex(row['stack']);caller=(int.from_bytes(raw[5:7],'little')+1)|raw[7]<<16
            if row['event']=='0013' and caller==0xc55970:rows.append(row)
        return rows
    all_events={}
    for label,voice,timing,_,_ in definitions:
        folder,rc=results[label];checks[label+'_exit']=rc==0
        all_events[label]=events(folder);checks[label+'_one_natural_pickup']=len(all_events[label])==1
        driver=list(csv.DictReader((folder/'driver.csv').open()));sun=[r for r in driver if r['selector']=='19' and r['value']=='15']
        # The retained route has no bonus-bug PCM15 before this encounter.
        checks[label+'_voice_source_independent']=len(sun)==(1 if voice=='md' else 0)
        timing_rows=list(csv.DictReader((folder/'timing.csv').open())) if (folder/'timing.csv').exists() else []
        checks[label+'_timing_source_independent']=bool(timing_rows)==(timing=='md') and all(r['before']=='4' and r['after']=='5' for r in timing_rows)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['both_modes_all2800_guest_fields']=len(hashes(results['both'][0]))==2800 and hashes(results['both'][0])==hashes(results['both-lle'][0])
    for name in ('audio.wav','window.png','scene.json','driver.csv','timing.csv'):checks['both_modes_'+name]=digest(results['both'][0]/name)==digest(results['both-lle'][0]/name)
    checks['timing_keeps_native_pickup_audio']=digest(results['native'][0]/'audio.wav')==digest(results['timing'][0]/'audio.wav')
    checks['voice_changes_audio']=digest(results['native'][0]/'audio.wav')!=digest(results['voice'][0]/'audio.wav')
    checks['voice_works_with_native_level_music']=any(r['value']=='15' and r['selector']=='19' for r in csv.DictReader((results['voice-native-music'][0]/'driver.csv').open()))
    field_sets={label:[r['frame'] for r in values] for label,values in all_events.items()}
    checks['pickup_contact_field_preserved']=all(field_sets[label]==field_sets['native'] for label in ('voice','timing','both','both-lle'))
    # One ordinary same-build resume proves the selected countdown/voice path.
    state=results['both'][0]/'active.state';tree=[json.loads(r) for r in (results['both'][0]/'tree.jsonl').read_text().splitlines()]
    row=next(r for r in tree if r['field']==2510);suffix=out/'resume.polled.tape';suffix.write_bytes(tape.read_bytes()[row['poll_index']*2:])
    folder=out/'resume';folder.mkdir();cmd=commands['both'].copy();i=cmd.index('--save-at');del cmd[i:i+3];cmd+=['--load',str(state)]
    cmd[cmd.index('--input-polled')+1]=str(suffix)
    for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
    for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
    commands['resume']=cmd
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    checks['current_build_resume_exit']=rc==0
    checks['current_build_resume_guest_fields']=hashes(folder)==[r for r in hashes(results['both'][0]) if int(r[0])>2510]
    for name in ('window.png','scene.json'):checks['resume_'+name]=digest(folder/name)==digest(results['both'][0]/name)
    checks['resume_remaining_pcm']=pcm(results['both'][0]/'audio.wav').endswith(pcm(folder/'audio.wav'))
    paths=[Path(__file__),build_path,approach_path,tape,state]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,pickup_fields=field_sets,
                cross_build_save_compatibility_tested=False,natural_input_no_guest_edits=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],field_sets,flush=True)


if __name__=='__main__':main()
