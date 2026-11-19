"""Exercise gorilla idle/jump/attack artwork through the nearby encounter route."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
out=ROOT/'build/hakuna808-encounter';out.mkdir(exist_ok=True)
cmd=json.loads((ROOT/'build/hakuna790-route/report.json').read_text())['cases'][1]['command'].copy();cmd[0]=str(ROOT/'build/hakuna802/player.exe');state=native_fixture(ROOT/'build/hakuna790-route/31000/current.state',out/'entry.native.state',31000)
profile=(ROOT/'build/hakuna803-gorilla/both/resources.ini').read_text()+'\ngraphics.sprites.simba.cub.frames = md\ngraphics.sprites.simba.cub.palette = md\ngraphics.sprites.simba.adult.frames = md\ngraphics.scenery.background = md\ngraphics.scenery.palettes = md\n';(out/'resources.ini').write_text(profile);(out/'host.ini').write_text('opengl = 0\nscale = 1\n')
for flag,value in (('--load',state),('--frames',36500),('--hash-at',36500),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--sprite-assets',ROOT/'build/hakuna801-helper/sprites.assets'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
i=cmd.index('--save-at');cmd[i+1:i+3]=['34220',str(out/'before-gorilla.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(out/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());sprites=json.loads((out/'sprites.json').read_text());checks=dict(complete_encounter_healthy=s['latched_gameplay']['health']>0 and s['level']==6,adult_destiny=s['latched_gameplay']['age']==65535,gorilla_pose_coverage=sprites['seen_by_role']['gorilla']>=30,useful_nearby_save=(out/'before-gorilla.state').exists())
paths=[Path(__file__),ROOT/'build/hakuna802/build-report.json',ROOT/'build/hakuna801-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,level=s['level'],gameplay=s['latched_gameplay'],seen_gorilla_frames=sprites['seen_by_role']['gorilla'],seen_mapped_frames=sprites['seen_mapped_frames'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,sprites['seen_by_role']['gorilla'],flush=True)
