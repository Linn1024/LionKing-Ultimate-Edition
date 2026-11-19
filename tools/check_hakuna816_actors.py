"""Direct checkpoint segments verify later actor sources and preserve gameplay."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
from pride_arena_history import bound
out=ROOT/'build/hakuna816-actors';out.mkdir(exist_ok=True);cases={};checks={}
base=json.loads((ROOT/'build/hakuna796-simba/report.json').read_text())['cases']['5-native']['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
settings=dict(native='',frames='graphics.sprites.enemies.other.frames = md\ngraphics.sprites.world_objects.frames = md\ngraphics.sprites.animals.monkeys.frames = md\ngraphics.sprites.pickups.frames = md\ngraphics.sprites.effects.defeat_puff.frames = md\n',palette='graphics.sprites.enemies.other.palette = md\ngraphics.sprites.world_objects.palette = md\ngraphics.sprites.animals.monkeys.palette = md\ngraphics.sprites.pickups.palette = md\ngraphics.sprites.effects.defeat_puff.palette = md\n')
settings['both']=settings['frames']+settings['palette']
for level,start,end,source,tape in [(5,31000,31240,ROOT/'build/hakuna790-route/31000/current.state',ROOT/'build/hakuna790-route/34500/input.polled.tape'),(6,37000,38000,ROOT/'build/hakuna809-handoff/destiny.state',ROOT/'build/hakuna790-route/after37000.polled.tape')]:
 state=native_fixture(source,out/f'{level}.native.state',start)
 for name,extra in [('old',''),*settings.items()]:
  label=f'{level}-{name}';folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/hakuna802/player.exe' if name=='old' else 'build/hakuna815/player.exe'))
  for flag,value in (('--load',state),('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--sprite-assets',ROOT/('build/hakuna801-helper/sprites.assets' if name=='old' else 'build/hakuna814-helper/sprites.assets'))):cmd[cmd.index(flag)+1]=str(value)
  cmd+=['--input-polled',str(tape)];(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');profile=(ROOT/'build/hakuna796-simba/5-native/resources.ini').read_text();(folder/'resources.ini').write_text(profile+'\n'+extra)
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
  s=json.loads((folder/'scene.json').read_text());sp=json.loads((folder/'sprites.json').read_text());cases[label]=dict(command=cmd,level=s['level'],gameplay=s['latched_gameplay'],guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),seen=sp['seen_mapped_frames'],roles=sp.get('later_roles',{}));print(label,cases[label]['roles'],flush=True)
 imgs={k:Image.open(out/f'{level}-{k}/window.png').convert('RGB') for k in ('old',*settings)}
 checks[f'{level}/native_picture_preserved']=ImageChops.difference(imgs['old'],imgs['native']).getbbox() is None
 checks[f'{level}/guest_preserved']=len({tuple(sorted(c['guest'].items())) for k,c in cases.items() if k.startswith(str(level)+'-')})==1
 checks[f'{level}/healthy_scene']=all(c['level']==level and c['gameplay']['health']>0 for k,c in cases.items() if k.startswith(str(level)+'-'))
 checks[f'{level}/owned_images_used']=cases[f'{level}-frames']['seen']>0 and cases[f'{level}-native']['seen']==0
 checks[f'{level}/world_images_used']=cases[f'{level}-frames']['roles']['world']>0
 checks[f'{level}/source_choices_distinct']=ImageChops.difference(imgs['native'],imgs['both']).getbbox() is not None
 if level==6:checks['destiny_monkeys_used']=cases['6-frames']['roles']['destiny_monkeys']>0;checks['destiny_jaguars_used']=cases['6-frames']['roles']['enemies']>0
paths=[Path(__file__),ROOT/'build/hakuna815/build-report.json',ROOT/'build/hakuna814-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
