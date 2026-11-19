"""One ordinary idle continuation at the existing final fight; no forced enemy state or gameplay change."""
import csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard544-fight/report.json';r=bound(reference);build=ROOT/'build/graveyard609/build-report.json';bound(build)
out=ROOT/'build/graveyard611-taunt';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3];i=cmd.index('--input-polled');del cmd[i:i+2];zero=out/'idle.tape';zero.write_bytes(bytes(18600*2));cmd+=['--input',str(zero),'--wav',str(out/'audio.wav'),'--wav-seconds','8']
for flag,value in (('--load',str(reference.parent/'enemies.state')),('--frames','18500'),('--hash-at','18500'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\naudio.music.elephant_graveyard = md\naudio.effects.world.hyena_taunt = md\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_HYENA_TAUNT_TRACE=str(out/'taunts.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
calls=[x for x in csv.DictReader((out/'commands.csv').open()) if x['selector']=='19' and x['value']=='3'];paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='TAUNT_EXERCISED' if calls else 'TAUNT_NOT_EXERCISED',command=cmd,count=len(calls),scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('TAUNTS',len(calls),flush=True)
