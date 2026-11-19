"""Author reusable native fatal-hit fixtures with one research health cap."""
import os,json,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna844-deaths';out.mkdir(exist_ok=True);cases={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in (5,6):
 folder=out/str(level);folder.mkdir(exist_ok=True)
 if level==5:
  cmd=json.loads((ROOT/'build/hakuna843-fatal/report.json').read_text())['cases']['5']['command'].copy();stop=36430
 else:
  cmd=json.loads((ROOT/'build/hakuna838-health/report.json').read_text())['cases']['6']['command'].copy();stop=40000
 cmd[0]=str(ROOT/'build/hakuna841-health/player.exe')
 for flag,value in (('--frames',stop),('--hash-at',stop),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n');cmd+=['--save-at',str(stop),str(folder/'checkpoint.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'controller.csv').open()));deaths=[r for r in rows if r['health']=='0'];cases[str(level)]=dict(command=cmd,zero_health=deaths[:8],last=rows[-1]);print(level,cases[str(level)]['zero_health'],flush=True)
 if level==5:native_fixture(folder/'checkpoint.state',folder/'before.native.state',stop)
paths=[Path(__file__),ROOT/'build/hakuna841-health/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
