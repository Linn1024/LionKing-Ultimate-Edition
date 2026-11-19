"""Observe native nonfinal death at safe saved positions with research health0."""
import os,json,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna840-zero';out.mkdir(exist_ok=True);cases={}
base=json.loads((ROOT/'build/hakuna830-hud/report.json').read_text())['cases']['native']['command']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start,path in [(5,31000,'build/hakuna816-actors/5.native.state'),(6,38000,'build/hakuna796-simba/6.native.state')]:
 folder=out/str(level);folder.mkdir(exist_ok=True);state=native_fixture(ROOT/path,folder/'entry.native.state',start);cmd=base.copy();cmd[0]=str(ROOT/'build/hakuna839-zero/player.exe')
 for flag,value in (('--load',state),('--frames',start+650),('--hash-at',start+650),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n');cmd+=['--input-polled',str(folder/'neutral.polled.tape'),'--save-at',str(start+50),str(folder/'death.state')];(folder/'neutral.polled.tape').write_bytes(bytes(3000))
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'controller.csv').open()));deaths=[r for r in rows if r['health']=='0'];cases[str(level)]=dict(command=cmd,zero_health=deaths[:12],last=rows[-1]);print(level,cases[str(level)]['zero_health'],flush=True)
paths=[Path(__file__),ROOT/'build/hakuna839-zero/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
