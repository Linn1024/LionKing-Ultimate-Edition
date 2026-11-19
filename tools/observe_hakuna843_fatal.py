"""Native fatal enemy hits with research health1; retain original damage/action logic."""
import os,json,subprocess,csv,struct
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna843-fatal';out.mkdir(exist_ok=True);cases={}
base=json.loads((ROOT/'build/hakuna830-hud/report.json').read_text())['cases']['native']['command']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,path,pad in [(5,'build/hakuna803-gorilla/encounter.native.state',0),(6,'build/hakuna796-simba/6.native.state',0x200)]:
 folder=out/str(level);folder.mkdir(exist_ok=True);d=(ROOT/path).read_bytes();start=struct.unpack_from('<I',d,12)[0];state=native_fixture(ROOT/path,folder/'entry.native.state',start);cmd=base.copy();cmd[0]=str(ROOT/'build/hakuna841-health/player.exe')
 for flag,value in (('--load',state),('--frames',start+1500),('--hash-at',start+1500),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n');cmd+=['--input-polled',str(folder/'input.polled.tape')];(folder/'input.polled.tape').write_bytes(struct.pack('<H',pad)*4000)
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'controller.csv').open()));deaths=[r for r in rows if r['health']=='0'];cases[str(level)]=dict(command=cmd,start=start,zero_health=deaths[:12],last=rows[-1]);print(level,cases[str(level)]['zero_health'],flush=True)
paths=[Path(__file__),ROOT/'build/hakuna841-health/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
