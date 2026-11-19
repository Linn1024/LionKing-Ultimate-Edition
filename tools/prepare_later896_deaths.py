"""Author native7/8 fatal-hit fixtures with the existing research-only health cap."""
import json,os,csv,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later896-deaths';out.mkdir(exist_ok=True);cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start in ((7,44500),(8,52000)):
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later885-choices/report.json').read_text())['cases'][f'{level}-native']['command'].copy();cmd[0]=str(ROOT/'build/hakuna841-health/player.exe')
 for flag,value in (('--frames',start+550),('--hash-at',start+550),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n')
 with (folder/'observe.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_CONTROLLER_TRACE=str(folder/'controller.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'controller.csv').open()));dead=next((r for r in rows if r['health']=='0' and r['action']=='c35a82'),None);assert dead,(level,rows[-5:]);stop=int(dead['frame'])-2
 for flag,value in (('--frames',stop),('--hash-at',stop)):cmd[cmd.index(flag)+1]=str(value)
 cmd+=['--save-at',str(stop),str(folder/'before.state')]
 with (folder/'prepare.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 used=int(re.search(r'tape_words_used=(\d+)',(folder/'prepare.log').read_text())[1]);tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(folder/'remaining.polled.tape').write_bytes(tape[used*2:]);native_fixture(folder/'before.state',folder/'before.native.state',stop);cases[str(level)]=dict(frame=stop,fatal=dead,command=cmd,used_polls=used);print(level,stop,dead,flush=True)
paths=[Path(__file__),ROOT/'build/hakuna841-health/report.json',ROOT/'build/later885-choices/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',scope='Research health1 cap only during fixture authoring. Published/native test players load the resulting pre-hit state without health injection; original damage and C35A82 fatal logic remain.',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
