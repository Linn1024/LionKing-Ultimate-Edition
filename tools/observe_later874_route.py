"""Continue from Return toward Pride Rock/ending once, retaining a final-level checkpoint."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later874-route';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later872-route/report.json').read_text())['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--load',ROOT/'build/later872-route/later.native.state'),('--input-polled',ROOT/'build/later872-route/after52000.polled.tape'),('--frames',61000),('--hash-at',61000),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','56500',str(out/'pride-rock.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_OBJECTS=str(out/'poses.csv'),TLK_BG_TRACE=str(out/'scenes.csv'),TLK_AUDIO_EVENTS=str(out/'audio.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
native_fixture(out/'pride-rock.state',out/'pride-rock.native.state',56500);s=json.loads((out/'scene.json').read_text());levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
poses=list(csv.DictReader((out/'poses.csv').open()));checks=dict(pride_rock_seen=any(r['level']==9 for r in levels),actors_observed=bool(poses),checkpoint=(out/'pride-rock.native.state').exists());paths=[Path(__file__),ROOT/'build/later872-route/report.json',ROOT/'build/later871-observer/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',checks=checks,scope='Native later-level actor inventory/progression; final screenshot and controller evidence must establish ending before any completion claim.',levels=levels,command=cmd,last_level=s['level'],gameplay=s['latched_gameplay'],pose_records=len(poses),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,levels,s['latched_gameplay'],flush=True)
