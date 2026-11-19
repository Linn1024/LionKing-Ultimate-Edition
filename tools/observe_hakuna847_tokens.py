"""Confirm gorilla recovery token at the real native animation parser."""
import json,os,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna847-tokens';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/hakuna843-fatal/report.json').read_text())['cases']['5']['command'].copy();cmd[0]=str(ROOT/'build/hakuna835-observer/player.exe')
for flag,value in (('--frames',36500),('--hash-at',36500),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_LATER_GORILLA_TOKENS=str(out/'tokens.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
rows=list(csv.DictReader((out/'tokens.csv').open()));recovery=[r for r in rows if r['cursor']=='c27d43'];alternate=[r for r in rows if r['cursor']=='c27d9d'];checks=dict(normal_recovery_observed=bool(recovery),loaded59=all(r['value']=='59' for r in recovery));paths=[Path(__file__),ROOT/'build/hakuna835-observer/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,normal_recovery=recovery,alternate=alternate,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,recovery,flush=True)
