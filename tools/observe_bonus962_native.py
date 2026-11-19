"""Direct native bonus starts, nearby fixtures and actual actor/layer inventories."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus962-native';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/pride931-choices/report.json').read_text())['cases']['9-native']['command'].copy();base[0]=str(ROOT/'build/bonus960-observer/player.exe')
for flag in ('--load','--input-polled'):
 i=base.index(flag);del base[i:i+2]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={}
for level in range(10,14):
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=base.copy();cmd+=['--practice-level',str(level),'--save-at','1900',str(folder/'bonus.state')]
 for flag,value in (('--frames',2050),('--hash-at',2050),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--sprite-assets',ROOT/'build/pride928-helper/sprites.assets'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_OBJECTS=str(folder/'poses.csv'),TLK_BG_TRACE=str(folder/'scenes.csv'),TLK_AUDIO_EVENTS=str(folder/'audio.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 native_fixture(folder/'bonus.state',folder/'bonus.native.state',1900);s=json.loads((folder/'scene.json').read_text());cases[str(level)]=dict(command=cmd,actual_level=s['level'],gameplay=s['latched_gameplay'],layers=s['layers'],pose_records=sum(1 for _ in csv.DictReader((folder/'poses.csv').open())));print(level,s['level'],s['latched_gameplay'],cases[str(level)]['pose_records'],flush=True)
paths=[Path(__file__),ROOT/'build/bonus960-observer/report.json'];(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
