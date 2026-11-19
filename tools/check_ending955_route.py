"""Continue the native ending from the nearby victory checkpoint, without replaying levels."""
import json,os,csv,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/ending955-route';out.mkdir(exist_ok=True);prior=ROOT/'build/pride933-route/report.json';cmd=json.loads(prior.read_text())['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3];i=cmd.index('--input-polled');del cmd[i:i+2];cmd[0]=str(ROOT/'dist/installed-preview949/LionKing.exe')
for flag,value in (('--load',prior.parent/'ending.native.state'),('--frames',71000),('--hash-at',71000),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','70000',str(out/'ending.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_BG_TRACE=str(out/'scenes.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
native_fixture(out/'ending.state',out/'ending.native.state',70000);s=json.loads((out/'scene.json').read_text());scenes=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 key=(int(r['level']),int(r['descriptor']))
 if not scenes or tuple(scenes[-1]['scene'])!=key:scenes.append(dict(frame=int(r['frame']),scene=key))
paths=[Path(__file__),prior,ROOT/'build/pride949/build-report.json'];(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,scenes=scenes,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(scenes,s['latched_gameplay'],flush=True)
