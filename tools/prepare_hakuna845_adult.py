"""Retain the known native adult pre-fatal-hit checkpoint for focused music checks."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna845-adult';out.mkdir(exist_ok=True);r=json.loads((ROOT/'build/hakuna844-deaths/report.json').read_text());cmd=r['cases']['6']['command'].copy();frame=int(r['cases']['6']['zero_health'][0]['frame'])-2
for flag,value in (('--frames',frame),('--hash-at',frame),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
i=cmd.index('--save-at');cmd[i+1:i+3]=[str(frame),str(out/'before.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
native_fixture(out/'before.state',out/'before.native.state',frame)
(out/'report.json').write_text(json.dumps(dict(result='PREPARED',frame=frame,command=cmd,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),ROOT/'build/hakuna844-deaths/report.json']}),indent=2)+'\n');print('PREPARED',frame,flush=True)
