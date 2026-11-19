"""Create one reusable current-build ride checkpoint instead of replaying level1 per check."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait449-ostrich/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/cant-wait452-checkpoint';out.mkdir(exist_ok=True)
cmd=ref['commands']['md'].copy();cmd[0]=str(ROOT/'dist/installed-preview448/LionKing.exe')
state=out/'ostrich-ride.state';cmd+=['--save-at','7000',str(state)]
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','seed.png'),('--dump-scene','seed-scene.json')):
    old=Path(cmd[cmd.index(flag)+1]);cmd[cmd.index(flag)+1]=str(out/name)
    if flag in ('--config','--resource-profile'):(out/name).write_bytes(old.read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'seed.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=75,creationflags=subprocess.CREATE_NO_WINDOW)
text=(out/'seed.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',text)[1]);tape=Path(cmd[cmd.index('--input-polled')+1]);tail=out/'remaining.polled.tape';tail.write_bytes(tape.read_bytes()[used*2:])
resume=cmd.copy();i=resume.index('--save-at');del resume[i:i+3];resume+=['--load',str(state)]
resume[resume.index('--frames')+1]='7008';resume[resume.index('--hash-at')+1]='7008';resume[resume.index('--input-polled')+1]=str(tail)
resume[resume.index('--dump-window')+1]=str(out/'resumed.png');resume[resume.index('--dump-scene')+1]=str(out/'resumed-scene.json')
with (out/'resume.log').open('wb') as log:subprocess.run(resume,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'resumed-scene.json').read_text());checks=dict(state_created=state.is_file(),correct_polled_tail=tail.stat().st_size>0,loaded_second_level=scene['level']==1 and scene['latched_gameplay']['descriptor']==0x3b9,ostrich_present=any(p.get('actor_descriptor') in (0xc58c20,0xc58c2c) for p in scene['pieces']))
paths=[Path(__file__),reference,Path(cmd[0])]
(out/'report.json').write_text(json.dumps(dict(result='READY' if all(checks.values()) else 'FAIL',checks=checks,seed_command=cmd,resume_command=resume,field=7000,used_polled_words=used,binary_sha256=digest(Path(cmd[0])),scope='One-time ordinary route creates a current-build second-level ride checkpoint. Future local rendering checks start with resume_command and correctly sliced controller input; use direct level select for earlier sections. No old-build compatibility or repeated progression test.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print('CHECKPOINT_READY',checks,'polls',used,flush=True)
