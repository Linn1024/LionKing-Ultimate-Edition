"""Author a current early Graveyard checkpoint and locate its first ordinary controller input."""
import gzip,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard490-entry/report.json';r=bound(reference)
build=ROOT/'build/graveyard503/build-report.json';bound(build)
out=ROOT/'build/graveyard505-entry';out.mkdir(exist_ok=True);cmd=r['commands']['md'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,value in (('--frames','1530'),('--hash-at','1530'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
i=cmd.index('--save-at');del cmd[i:i+3];cmd+=['--save-at','1530',str(out/'entry.state')]
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.hud = md\naudio.music.elephant_graveyard = md\naudio.music.stampede = md\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
try:
    with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
finally:metadata=trace.finish()
rows=[json.loads(x) for x in gzip.open(out/'tree.jsonl.gz','rt')];actual=[x for x in rows if x['level']==2 and x['descriptor']==0xc003eb and x['health']>0]
events=[];last=None
for row in rows:
    key=tuple(row[k] for k in ('level','descriptor','health','macro_index','macro_length'))
    if key!=last and row['level']==2:events.append({k:row[k] for k in ('field','level','descriptor','health','macro_index','macro_length')})
    last=key
scene=json.loads((out/'scene.json').read_text());paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='ENTRY_AUTHORED',command=cmd,scene=scene['latched_gameplay'],first_owned=actual[0] if actual else None,last_owned=actual[-1] if actual else None,events=events,trace_metadata=metadata,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(scene['latched_gameplay'],events[-12:],flush=True)
