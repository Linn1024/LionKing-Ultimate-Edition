"""Inventory the next stages once from the current Be Prepared checkpoint."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later872-route';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/destiny863-handoff/report.json').read_text())['command'].copy();cmd[0]=str(ROOT/'build/later871-observer/player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--load',ROOT/'build/destiny863-handoff/be-prepared.native.state'),('--input-polled',ROOT/'build/destiny863-handoff/after44500.polled.tape'),('--frames',52000),('--hash-at',52000),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','52000',str(out/'current.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery.background = md\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_OBJECTS=str(out/'poses.csv'),TLK_BG_TRACE=str(out/'scenes.csv'),TLK_AUDIO_EVENTS=str(out/'audio.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
used=int(re.search(r'tape_words_used=(\d+)',(out/'run.log').read_text())[1]);tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(out/'after52000.polled.tape').write_bytes(tape[used*2:]);native_fixture(out/'current.state',out/'later.native.state',52000)
levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
s=json.loads((out/'scene.json').read_text());poses=list(csv.DictReader((out/'poses.csv').open()));checks=dict(entered_later_level=any(r['level']>=8 for r in levels),healthy=s['latched_gameplay']['health']>0,actors_observed=bool(poses),useful_next_checkpoint=(out/'later.native.state').exists())
paths=[Path(__file__),ROOT/'build/later871-observer/report.json',ROOT/'build/destiny863-handoff/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,scope=__doc__,levels=levels,pose_records=len(poses),command=cmd,used_polls=used,last_level=s['level'],gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,levels,s['latched_gameplay'],flush=True)
