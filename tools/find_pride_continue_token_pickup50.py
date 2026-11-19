"""Find a normal-input Sun pickup using a fresh current-build checkpoint."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token-behavior50';build_path=base/'build-report.json';build=bound(build_path)
    source=ROOT/'build/pride-continue-token47/full-route/report.json';prior=bound(source)
    out=base/'pickup-approach';out.mkdir();template=prior['commands']['aot'].copy();template[0]=str(base/'player.exe')
    i=template.index('--hash-at');del template[i:i+2]
    commands={};checks={};cases=[]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    profile=Path(template[template.index('--resource-profile')+1]).read_text()+'\naudio.effects.world.continue_token = snes\ngameplay.levels.pride_lands.continue_token_animation = snes\n'
    def run(label,frames,tape=None,state=None,save=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        (folder/'host.ini').write_bytes(Path(template[template.index('--config')+1]).read_bytes());(folder/'resources.ini').write_text(profile)
        cmd[cmd.index('--config')+1]=str(folder/'host.ini');cmd[cmd.index('--resource-profile')+1]=str(folder/'resources.ini');cmd[cmd.index('--frames')+1]=str(frames)
        if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
        if state:cmd+=['--load',str(state)]
        if save:cmd+=['--save-at',str(frames),str(folder/'saved.state')]
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label,rc,flush=True);assert rc==0,(label,(folder/'run.log').read_text()[-500:]);return folder
    seed=run('fresh-seed',2505,save=True);row=json.loads((seed/'tree.jsonl').read_text().splitlines()[-1])
    checks['fresh_current_build_checkpoint']=row['field']==2505 and row['level']==0 and len(row['choices'])==130
    def caller(row):
        raw=bytes.fromhex(row['stack']);return int.from_bytes(raw[5:7],'little')+1 | raw[7]<<16
    selected=None
    for right in range(0,31,5):
        tape=out/f'right-{right}.tape';tape.write_bytes(struct.pack('<H',0x100)*right+bytes(1600))
        folder=run(f'right-{right}',2700,tape,seed/'saved.state')
        events=[r for r in csv.DictReader((folder/'events.csv').open()) if r['event']=='0013' and caller(r)==0xc55970]
        cases.append(dict(right_polls=right,events=events))
        if events:selected=dict(right_polls=right,event_field=int(events[0]['frame']),tail_tape=tape.relative_to(ROOT).as_posix());break
    checks['ordinary_pickup_found']=selected is not None
    paths=[Path(__file__),build_path,source,seed/'saved.state']
    report=dict(result='PASS' if all(checks.values()) else 'SEARCH_INCOMPLETE',checks=checks,commands=commands,cases=cases,selected=selected,
                prefix_poll_count=row['poll_index'],original_tape=template[template.index('--input-polled')+1],
                same_build_checkpoint_only=True,guest_memory_or_register_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,selected,flush=True)


if __name__=='__main__':main()
