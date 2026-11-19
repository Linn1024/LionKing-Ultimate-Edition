"""Replay the Available MD route with the existing MD-menu input prefix."""
import gzip,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/pride404-preset-route/report.json';r=bound(reference)
prefix_report=ROOT/'build/pride-restart-prefix-spaced99/report.json';pr=bound(prefix_report)
prefix_tape=Path(pr['command'][pr['command'].index('--input-polled')+1])
original=Path(r['command'][r['command'].index('--input-polled')+1])
out=ROOT/'build/pride406-preset-route';out.mkdir(exist_ok=True)
tape=out/'ordinary.polled.tape';tape.write_bytes(prefix_tape.read_bytes()[:737*2]+original.read_bytes()[638*2:])
cmd=r['command'].copy();cmd[cmd.index('--input-polled')+1]=str(tape);cmd[cmd.index('--frames')+1]='6000';cmd[cmd.index('--hash-at')+1]='1500,2200,4500,6000'
i=cmd.index('--save-at');cmd[i+1]='6000';cmd[i+2]=str(out/'endpoint.state')
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_SOFT_TREE_LOG=trace.name)
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
metadata=trace.finish();first=None;events=[];last=None
for line in gzip.open(out/'tree.jsonl.gz','rt'):
    row=json.loads(line)
    if not first and row['descriptor']==0xc00387 and row['level']==0:first={key:row[key] for key in ('field','poll_index','difficulty','health','lives')}
    key=tuple(row[name] for name in ('level','descriptor','difficulty','lives','health'))
    if key!=last:events.append({name:row[name] for name in ('field','poll_index','level','descriptor','difficulty','lives','health')});last=key
scene=json.loads((out/'scene.json').read_text());game=scene['latched_gameplay']
checks=dict(exit=rc==0,exact_available_md_profile=(out/'resources.ini').read_bytes()==(reference.parent/'resources.ini').read_bytes(),gameplay_controller_suffix_unchanged=tape.read_bytes()[737*2:]==original.read_bytes()[638*2:],easy_selected_by_ordinary_options=bool(first) and first['difficulty']==0,profile_accepted='Saved resource profile loaded' in (out/'run.log').read_text(),first_level_completed=scene['level']==1)
paths=[Path(__file__),reference,prefix_report,prefix_tape,original]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE_ROUTE',checks=checks,command=cmd,first_pride=first,events=events,endpoint=dict(level=scene['level'],gameplay=game,camera=scene['camera']),trace_metadata=metadata,scope='Ordinary power-on Available MD route. Correct pre-existing MD navigation prefix selects Easy, retaining the prior gameplay suffix exactly. No game/ROM edits or source reduction; credited movie-derived input remains local.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,first,scene['level'],game,flush=True)
