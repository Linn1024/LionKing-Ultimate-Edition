"""Finish the nearby gorilla encounter with selected MD recovery and resources."""
import json,os,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna856-selected';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/hakuna809-handoff/report.json').read_text())['command'].copy();cmd[0]=str(ROOT/'build/hakuna849/player.exe')
for flag,value in (('--config',out/'host.ini'),('--resource-profile',ROOT/'profiles/hakuna-md.ini'),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
i=cmd.index('--save-at');cmd[i+2]=str(out/'destiny.state');(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_GORILLA_TIMING=str(out/'gorilla.csv'),TLK_MD_SOUND_COMMANDS=str(out/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=35,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());timing=list(csv.DictReader((out/'gorilla.csv').open())) if (out/'gorilla.csv').exists() else [];checks=dict(healthy_destiny=s['level']==6 and s['latched_gameplay']['age']==65535 and s['latched_gameplay']['health']>0,selected_boss_pause_exercised=bool(timing),useful_checkpoint=(out/'destiny.state').exists());paths=[Path(__file__),ROOT/'build/hakuna849/build-report.json',ROOT/'profiles/hakuna-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,gameplay=s['latched_gameplay'],timing=timing,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,s['latched_gameplay'],flush=True)
