"""Retain the7 fixture and author Return fatal contact with a neutral input branch."""
import csv,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride935-death';out.mkdir(exist_ok=True);cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
folder=out/'9';folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/pride931-choices/report.json').read_text())['cases']['9-native']['command'].copy();tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(folder/'branch.polled.tape').write_bytes(struct.pack('<80H',*[0x200]*80)+bytes(8000));cmd[0]=str(ROOT/'build/hakuna841-health/player.exe');cmd[cmd.index('--load')+1]=str(ROOT/'build/later904-fallback/pride-rock.native.state')
for flag,value in (('--input-polled',folder/'branch.polled.tape'),('--frames',3200),('--hash-at',3200),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (folder/'observe.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
rows=list(csv.DictReader((folder/'controller.csv').open()));dead=next((r for r in rows if r['health']=='0' and r['action']=='c35a82'),None);assert dead,rows[-5:];stop=int(dead['frame'])-2
for flag,value in (('--frames',stop),('--hash-at',stop)):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at',str(stop),str(folder/'before.state')]
with (folder/'prepare.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
used=int(re.search(r'tape_words_used=(\d+)',(folder/'prepare.log').read_text())[1]);(folder/'remaining.polled.tape').write_bytes((folder/'branch.polled.tape').read_bytes()[used*2:]);native_fixture(folder/'before.state',folder/'before.native.state',stop);cases['9']=dict(frame=stop,fixture=str(folder/'before.native.state'),tape=str(folder/'remaining.polled.tape'),fatal=dead,command=cmd);paths=[Path(__file__),ROOT/'build/hakuna841-health/report.json',ROOT/'build/pride931-choices/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',scope='Research-only health cap authoring; original native enemy contact and fatal controller. New runtime players have no health injection.',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PREPARED',[(k,r['frame']) for k,r in cases.items()],flush=True)
