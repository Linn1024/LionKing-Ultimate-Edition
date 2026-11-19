"""Locate the old recording's menu/game start with the Available MD preset."""
import gzip,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/pride404-preset-route/report.json';r=bound(reference)
out=ROOT/'build/pride405-start';out.mkdir(exist_ok=True);cmd=r['command'].copy()
for flag,n in (('--wav',2),('--save-at',3),('--dump-window',2)):
    i=cmd.index(flag);del cmd[i:i+n]
cmd[cmd.index('--frames')+1]='1500';cmd[cmd.index('--hash-at')+1]='1500'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
cmd[cmd.index('--dump-scene')+1]=str(out/'scene.json');cmd+=['--save-at','1500',str(out/'start.state')]
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_SOFT_TREE_LOG=trace.name)
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
metadata=trace.finish();rows=[json.loads(line) for line in gzip.open(out/'tree.jsonl.gz','rt')];events=[];previous=None
for row in rows:
    key=tuple(row[name] for name in ('level','descriptor','difficulty','lives','health'))
    if key!=previous:events.append({name:row[name] for name in ('field','poll_index','level','descriptor','difficulty','lives','health')});previous=key
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED' if rc==0 else 'FAIL',command=cmd,events=events,trace_metadata=metadata,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(events[-15:],flush=True)
