"""Check actual spiders/frogs at Hakuna's nearby opening, not earlier levels."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna817-opening';out.mkdir(exist_ok=True)
cmd=json.loads((ROOT/'build/hakuna816-actors/report.json').read_text())['cases']['5-both']['command'].copy()
for flag,value in (('--load',ROOT/'build/hakuna781-native/entry.native.state'),('--input-polled',ROOT/'build/hakuna781-native/after27000.polled.tape'),('--frames',28500),('--hash-at',28500),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');cmd+=['--save-at','28200',str(out/'spiders.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(out/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());sp=json.loads((out/'sprites.json').read_text());checks=dict(correct_healthy_scene=s['level']==5 and s['latched_gameplay']['health']>0,enemy_images_used=sp['later_roles']['enemies']>=8,nearby_spider_checkpoint=(out/'spiders.state').exists())
paths=[Path(__file__),ROOT/'build/hakuna815/build-report.json',ROOT/'build/hakuna814-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,roles=sp['later_roles'],gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,sp['later_roles'],flush=True)
