"""Verify scene-owned Simba source choices using nearby cub/adult checkpoints."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
from pride_arena_history import bound
out=ROOT/'build/hakuna796-simba';out.mkdir(exist_ok=True);bound(ROOT/'build/hakuna795/build-report.json');cases={};checks={}
base=json.loads((ROOT/'build/hakuna789-player/report.json').read_text())['cases']['5-native']['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,frame,source,age in ((5,31000,ROOT/'build/hakuna790-route/31000/current.state','cub'),(6,38000,ROOT/'build/hakuna781-native/38000.state','adult')):
 state=native_fixture(source,out/f'{level}.native.state',frame)
 for name,extra in [('old',''),('native',''),('frames',f'graphics.sprites.simba.{age}.frames = md\n'),('palette',f'graphics.sprites.simba.{age}.palette = md\n'),('both',f'graphics.sprites.simba.{age}.frames = md\ngraphics.sprites.simba.{age}.palette = md\n')]:
  label=f'{level}-{name}';folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/hakuna786/player.exe' if name=='old' else 'build/hakuna795/player.exe'))
  for flag,value in (('--load',state),('--frames',frame+60),('--hash-at',frame+60),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
  (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');profile=(ROOT/'build/hakuna789-player/5-native/resources.ini').read_text();(folder/'resources.ini').write_text(profile+'\n'+extra)
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
  text=(folder/'run.log').read_text();s=json.loads((folder/'scene.json').read_text());sprites=json.loads((folder/'sprites.json').read_text());cases[label]=dict(command=cmd,guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',text,re.M)),level=s['level'],gameplay=s['latched_gameplay'],seen=sprites['seen_mapped_frames']);print(label,'seen',sprites['seen_mapped_frames'],flush=True)
 imgs={name:Image.open(out/f'{level}-{name}/window.png').convert('RGB') for name in ('old','native','frames','palette','both')}
 scene=json.loads((out/f'{level}-native/scene.json').read_text());mask=Image.new('L',imgs['native'].size);draw=ImageDraw.Draw(mask);column=(imgs['native'].width-256)//2
 for p in scene['pieces']:
  if p['position_pointer']==0xb21b and not p['fixed']:
   x,y=p['screen'];sz=p['size'];draw.rectangle((x+column-8,y-8,x+column+sz+8,y+sz+8),fill=255)
 checks[f'{level}/native_preserved']=ImageChops.difference(imgs['old'],imgs['native']).getbbox() is None
 checks[f'{level}/guest_preserved']=len({tuple(sorted(c['guest'].items())) for k,c in cases.items() if k.startswith(str(level)+'-')})==1
 checks[f'{level}/actual_owned_images_used']=cases[f'{level}-frames']['seen']>0 and cases[f'{level}-both']['seen']>0 and cases[f'{level}-native']['seen']==0
 checks[f'{level}/healthy_correct_scene']=all(c['level']==level and c['gameplay']['health']>0 for k,c in cases.items() if k.startswith(str(level)+'-'))
 for name in ('frames','palette','both'):
  diff=ImageChops.difference(imgs['native'],imgs[name]);diff.paste((0,0,0),(0,0),mask);checks[f'{level}/{name}_only_simba']=diff.getbbox() is None
 checks[f'{level}/palette_visible']=ImageChops.difference(imgs['native'],imgs['palette']).getbbox() is not None
paths=[Path(__file__),ROOT/'build/hakuna795/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
