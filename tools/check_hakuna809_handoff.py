"""Verify healthy Destiny after the encounter, without replaying Hakuna's approach."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna809-handoff';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/hakuna803-gorilla/report.json').read_text())['entry_command'];cmd=base.copy()
used=int(re.search(r'tape_words_used=(\d+)',(ROOT/'build/hakuna803-gorilla/entry.log').read_text())[1]);tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(out/'remaining.polled.tape').write_bytes(tape[used*2:]);(out/'host.ini').write_text('opengl = 0\nscale = 1\n')
i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--load',ROOT/'build/hakuna803-gorilla/encounter.native.state'),('--input-polled',out/'remaining.polled.tape'),('--frames',37000),('--hash-at',37000),('--config',out/'host.ini'),('--resource-profile',ROOT/'build/hakuna808-encounter/resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','37000',str(out/'destiny.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());checks=dict(healthy_adult_destiny=s['level']==6 and s['stage_detected'] and s['latched_gameplay']['age']==65535 and s['latched_gameplay']['health']>0,current_checkpoint=(out/'destiny.state').exists())
paths=[Path(__file__),ROOT/'build/hakuna808-encounter/report.json',ROOT/'build/hakuna803-gorilla/report.json',ROOT/'build/hakuna802/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,s['latched_gameplay'],flush=True)
