"""Finish Destiny from its nearby entry and retain a next-level checkpoint."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/destiny818-route';out.mkdir(exist_ok=True)
cmd=json.loads((ROOT/'build/hakuna816-actors/report.json').read_text())['cases']['6-both']['command'].copy()
profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()+'\ngraphics.sprites.simba.adult.frames = md\ngraphics.sprites.simba.adult.palette = md\ngraphics.scenery.background = md\ngraphics.scenery.palettes = md\ngraphics.hud.frames = md\n';(out/'resources.ini').write_text(profile);(out/'host.ini').write_text('opengl = 0\nscale = 1\n')
for flag,value in (('--frames',46000),('--hash-at',46000),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','44500',str(out/'later.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(out/'sprites.json'),TLK_BG_TRACE=str(out/'scenes.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=80,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());sp=json.loads((out/'sprites.json').read_text());levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
checks=dict(reached_next_main_stage=any(r['level']==7 for r in levels),healthy_at_end=s['latched_gameplay']['health']>0,next_checkpoint=(out/'later.state').exists(),jaguar_images_used=sp['later_roles']['enemies']>0,monkey_images_used=sp['later_roles']['destiny_monkeys']>0,world_objects_used=sp['later_roles']['world']>0)
paths=[Path(__file__),ROOT/'build/hakuna815/build-report.json',ROOT/'build/hakuna814-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,levels=levels,gameplay=s['latched_gameplay'],roles=sp['later_roles'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,levels,s['latched_gameplay'],flush=True)
