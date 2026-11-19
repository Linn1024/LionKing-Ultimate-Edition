"""Observe original native health-death controllers after one research health1 setup."""
import os,json,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna838-health';out.mkdir(exist_ok=True);cases={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start,end,path,ref in [(5,27000,31000,'build/hakuna781-native/entry.native.state','5-both'),(6,37000,42000,'build/hakuna809-handoff/adult.state','6-both')]:
 folder=out/str(level);folder.mkdir(exist_ok=True)
 # Reviewed native fixtures in the actor test provide exact per-poll offsets.
 cmd=json.loads((ROOT/'build/hakuna816-actors/report.json').read_text())['cases'][ref]['command'].copy()
 if level==5:cmd[cmd.index('--load')+1]=str(ROOT/path);cmd[cmd.index('--input-polled')+1]=str(ROOT/'build/hakuna781-native/after27000.polled.tape')
 cmd[0]=str(ROOT/'build/hakuna837-health/player.exe')
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n')
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'controller.csv').open()));deaths=[r for r in rows if r['health']=='0'];cases[str(level)]=dict(command=cmd,zero_health=deaths[:12],last=rows[-1]);print(level,cases[str(level)]['zero_health'],flush=True)
paths=[Path(__file__),ROOT/'build/hakuna837-health/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
