"""Observe current-build native checkpoint display timing after real contact.

Use one fresh same-build seed, then controller-neutral branches. This is an
animation observation, not a cross-build save compatibility test.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-checkpoint-native51-reference';out.mkdir()
    source=ROOT/'build/pride-continue-token-behavior50/completion/report.json'
    prior=bound(source);assert prior['result']=='PASS'
    build=ROOT/'build/pride-continue-token-behavior50/build-report.json';bound(build)
    template=prior['commands']['aot'].copy()
    i=template.index('--hash-at');del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    commands={}
    def run(label,frame,seed=None,lle=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/name)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
            cmd[cmd.index(flag)+1]=str(folder/name)
        cmd[cmd.index('--frames')+1]=str(frame)
        if seed:
            cmd+=['--load',str(seed)]
            cmd[cmd.index('--input-polled')+1]=str(out/'neutral.tape')
        else:cmd+=['--save-at',str(frame),str(folder/'contact.state')]
        if lle:cmd+=['--lle']
        commands[label]=cmd
        env=dict(clean,TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                           check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        scene=json.loads((folder/'scene.json').read_text())
        poses=sorted({p['pose'] for p in scene['pieces'] if p['pose'] in (0xc456de,0xc2fde1,0xc2fe18)})
        print(label,poses,flush=True)
        return dict(frame=frame,poses=poses)
    (out/'neutral.tape').write_bytes(bytes(4096))
    # Audio callbacks label the field in progress with the previous completed
    # host counter. Event3279 therefore appears in the completed3280 snapshot.
    seed=run('contact',3280);rows=list(csv.DictReader((out/'contact/events.csv').open()))
    events=[]
    for row in rows:
        stack=bytes.fromhex(row['stack'])
        caller=(int.from_bytes(stack[5:7],'little')+1)|(stack[7]<<16)
        if row['event']=='0013' and caller==0xc55785:events.append(row)
    assert len(events)==1 and events[0]['frame']=='3279',events
    state=out/'contact/contact.state'
    frames=list(range(3281,3305))+[3330]
    with ThreadPoolExecutor(max_workers=3) as pool:
        aot=list(pool.map(lambda f:run('aot-'+str(f),f,state),frames))
    probes=(3281,3286,3291,3296,3330)
    with ThreadPoolExecutor(max_workers=3) as pool:
        lle=list(pool.map(lambda f:run('lle-'+str(f),f,state,True),probes))
    checks=dict(genuine_checkpoint_contact=True,all_fields_have_one_checkpoint_pose=all(len(r['poses'])==1 for r in aot))
    for field in probes:
        for name in ('scene.json','window.png','audio.wav'):
            checks[f'{field}_{name}_mode_parity']=digest(out/f'aot-{field}'/name)==digest(out/f'lle-{field}'/name)
    paths=[Path(__file__),source,build,Path(template[0]),Path(template[template.index('--input-polled')+1]),
           ROOT/'engine/runner/tlk_checkpoint_role.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                contact_completed_field=3280,contact_audio_counter=3279,aot=aot,lle=lle,no_guest_or_rom_edits=True,
                cross_build_save_compatibility_tested=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True)


if __name__=='__main__':main()
