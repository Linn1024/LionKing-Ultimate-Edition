"""Try retained ordinary-route checkpoint once; no compatibility changes if unsuitable."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard505-entry/report.json';r=bound(reference)
state=ROOT/'build/graveyard-verification/moving.state';suffix=ROOT/'build/graveyard-verification/after13500.polled.tape';assert state.exists() and suffix.exists()
out=ROOT/'build/graveyard509-checkpoint';out.mkdir(exist_ok=True);cmd=r['command'].copy()
for flag,count in (('--save-at',3),('--practice-level',2)):
    i=cmd.index(flag);del cmd[i:i+count]
cmd+=['--load',str(state),'--input-polled',str(suffix),'--save-at','13501',str(out/'current.state')]
for flag,value in (('--frames','13501'),('--hash-at','13501'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_bytes((reference.parent/'host.ini').read_bytes());(out/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW).returncode
scene=json.loads((out/'scene.json').read_text()) if (out/'scene.json').exists() else {};usable=rc==0 and scene.get('level')==2 and scene.get('latched_gameplay',{}).get('descriptor')==0x3eb and scene['latched_gameplay']['health']>0
paths=[Path(__file__),reference,state,suffix,ROOT/'build/graveyard503/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='USABLE' if usable else 'UNSUITABLE',command=cmd,scene=scene.get('latched_gameplay'),scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('USABLE' if usable else 'UNSUITABLE',scene.get('latched_gameplay'),flush=True)
