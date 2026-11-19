"""Continue a current MD-gameplay save with a small ordinary controller timing adjustment."""
import json,os,struct,subprocess,sys
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard626-choices/report.json';r=bound(reference);name=sys.argv[1] if len(sys.argv)>1 else 'left6';extra=int(sys.argv[2]) if len(sys.argv)>2 else 6
out=ROOT/('build/graveyard628-finish/'+name);out.mkdir(parents=True,exist_ok=True);cmd=r['commands']['both'].copy();cmd[cmd.index('--load')+1]=str(reference.parent/'both/entry.state');tape=out/'finish.polled.tape';source=reference.parent/'both/remaining.polled.tape';tape.write_bytes(struct.pack('<H',512)*extra+source.read_bytes());cmd[cmd.index('--input-polled')+1]=str(tape)
for flag,value in (('--frames','19800'),('--hash-at','18000,19000,19800'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav'))):cmd[cmd.index(flag)+1]=value
i=cmd.index('--save-at');cmd[i+1:i+3]=['19800',str(out/'entry.state')]
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_bytes((ROOT/'build/graveyard623-gameplay/resources.ini').read_bytes())
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_GRAVEYARD_GAMEPLAY_TRACE=str(out/'gameplay.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=55,creationflags=subprocess.CREATE_NO_WINDOW)
metadata=trace.finish();scene=json.loads((out/'scene.json').read_text());last=trace.latest();checks=dict(living_stampede=last['level']==3 and last['descriptor']==0xc0041d and last['health']>0,no_life_lost=last['lives']==8)
paths=[Path(__file__),reference,source]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'NEEDS_INPUT_ADJUSTMENT',checks=checks,command=cmd,scene=scene['latched_gameplay'],last=last,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,scene['latched_gameplay'],flush=True)
