"""Continue the final level from its verified nearby checkpoint, retaining final-fight state."""
import json,os,csv,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride933-route';out.mkdir(exist_ok=True);prior=ROOT/'build/later902-selected/report.json';cmd=json.loads(prior.read_text())['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3];cmd[0]=str(ROOT/'build/pride929/player.exe')
for flag,value in (('--load',prior.parent/'pride-rock.native.state'),('--input-polled',prior.parent/'after57000.polled.tape'),('--frames',65000),('--hash-at',65000),('--sprite-assets',ROOT/'build/pride928-helper/sprites.assets'),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd[cmd.index('--resource-profile')+1]=str(ROOT/'profiles/pride-rock-md.ini')
cmd+=['--save-at','64000',str(out/'final-fight.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_BG_TRACE=str(out/'scenes.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
native_fixture(out/'final-fight.state',out/'ending.native.state',64000);s=json.loads((out/'scene.json').read_text());levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
paths=[Path(__file__),prior,ROOT/'build/pride929/build-report.json'];(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,levels=levels,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(levels,s['latched_gameplay'],flush=True)
