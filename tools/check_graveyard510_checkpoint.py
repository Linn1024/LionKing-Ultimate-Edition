"""Author one recording-compatible current checkpoint with its naturally collected upgrades.

The old retained checkpoint was unsuitable. This one-time prefix authors a fixture;
routine resource checks continue to use direct selection or this current save.
No guest edits, compatibility work, invulnerability or broad regression matrix.
"""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard505-entry/report.json';r=bound(reference)
out=ROOT/'build/graveyard510-checkpoint';out.mkdir(exist_ok=True);cmd=r['command'].copy()
for flag,count in (('--save-at',3),('--practice-level',2)):
    i=cmd.index(flag);del cmd[i:i+count]
source=ROOT/'engine/tapes/allbugsF.read.tape';cmd+=['--input-polled',str(source),'--save-at','13147',str(out/'entry.state')]
for flag,value in (('--frames','13147'),('--hash-at','13147'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=65,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'scene.json').read_text());checks=dict(actual_graveyard=scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb,natural_upgraded_health=scene['latched_gameplay']['health']==6,original_entry_position=scene['latched_gameplay']['player']==[1008,336])
paths=[Path(__file__),reference,source,ROOT/'build/graveyard503/build-report.json',ROOT/'build/graveyard509-checkpoint/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,scene=scene['latched_gameplay'],scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,scene['latched_gameplay'],flush=True)
