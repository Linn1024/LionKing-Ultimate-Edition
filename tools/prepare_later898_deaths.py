"""Retain the7 fixture and author Return fatal contact with a neutral input branch."""
import csv,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later898-deaths';out.mkdir(exist_ok=True);cases={};old=ROOT/'build/later896-deaths/7';data=(old/'before.native.state').read_bytes();frame=struct.unpack_from('<I',data,12)[0];assert frame==44823;fatal=next(r for r in csv.DictReader((old/'controller.csv').open()) if r['health']=='0' and r['action']=='c35a82');cases['7']=dict(frame=frame,fixture=str(old/'before.native.state'),tape=str(old/'remaining.polled.tape'),fatal=fatal)
folder=out/'8';folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later885-choices/report.json').read_text())['cases']['8-native']['command'].copy();tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(folder/'branch.polled.tape').write_bytes(tape[:200]+bytes(8000));cmd[0]=str(ROOT/'build/hakuna841-health/player.exe')
for flag,value in (('--input-polled',folder/'branch.polled.tape'),('--frames',53300),('--hash-at',53300),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (folder/'observe.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
rows=list(csv.DictReader((folder/'controller.csv').open()));dead=next((r for r in rows if r['health']=='0' and r['action']=='c35a82'),None);assert dead,rows[-5:];stop=int(dead['frame'])-2
for flag,value in (('--frames',stop),('--hash-at',stop)):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at',str(stop),str(folder/'before.state')]
with (folder/'prepare.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
used=int(re.search(r'tape_words_used=(\d+)',(folder/'prepare.log').read_text())[1]);(folder/'remaining.polled.tape').write_bytes((folder/'branch.polled.tape').read_bytes()[used*2:]);native_fixture(folder/'before.state',folder/'before.native.state',stop);cases['8']=dict(frame=stop,fixture=str(folder/'before.native.state'),tape=str(folder/'remaining.polled.tape'),fatal=dead,command=cmd);paths=[Path(__file__),ROOT/'build/hakuna841-health/report.json',old/'before.native.state',old/'remaining.polled.tape',old/'controller.csv']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',scope='Research-only health cap authoring; original native enemy contact and fatal controller. New runtime players have no health injection.',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PREPARED',[(k,r['frame']) for k,r in cases.items()],flush=True)
