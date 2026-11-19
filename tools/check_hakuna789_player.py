"""Bounded nearby scene checks: source independence, guest state and saved clock."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
from pride_arena_history import bound
out=ROOT/'build/hakuna789-player';out.mkdir(exist_ok=True);bound(ROOT/'build/hakuna786/build-report.json')
base=json.loads((ROOT/'build/hakuna781-native/report.json').read_text())['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={}
for level,frame,source in ((5,27000,ROOT/'build/hakuna778-checkpoint/entry.state'),(6,38000,ROOT/'build/hakuna781-native/38000.state')):
 state=native_fixture(source,out/f'{level}.native.state',frame)
 variants=[('old',''),('native',''),('background','graphics.scenery.background = md\n'),('md','graphics.scenery.background = md\ngraphics.scenery.palettes = md\n'),('palette','graphics.scenery.palettes = md\n')] if level==5 else [('native',''),('md','graphics.scenery.background = md\ngraphics.scenery.palettes = md\n')]
 for name,extra in variants:
  label=f'{level}-{name}';folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy()
  cmd[0]=str(ROOT/('dist/installed-preview771/LionKing.exe' if name=='old' else 'build/hakuna786/player.exe'))
  for flag,count in (('--input-polled',2),('--save-at',3)):
   while flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
  for flag,value in (('--load',state),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--frames',frame+180),('--hash-at',frame+180),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
  if name!='old':cmd[cmd.index('--asset-cache')+1]=str(ROOT/'build/hakuna787-helper/scenes.cache')
  profile=(ROOT/'profiles/exile-md.ini').read_text().replace('graphics = inherit','graphics = snes');(folder/'resources.ini').write_text(profile+'\n'+extra)
  (folder/'host.ini').write_text('opengl = 0\nscale = 1\n')
  if label=='5-md':cmd+=['--save-at',str(frame+100),str(out/'current-waterfall.state')]
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
  text=(folder/'run.log').read_text();scene=json.loads((folder/'scene.json').read_text());cases[label]=dict(command=cmd,frame_sha256=re.findall(r'^frame_sha256=(\w+)',text,re.M)[-1],wram_sha256=re.findall(r'^wram_sha256=(\w+)',text,re.M)[-1],scene=scene['latched_gameplay'],level=scene['level'],waterfall=scene.get('hakuna_waterfall'))
  print(label,scene.get('hakuna_waterfall'),flush=True)
cmd=cases['5-md']['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3];cmd[cmd.index('--load')+1]=str(out/'current-waterfall.state');cmd[cmd.index('--dump-window')+1]=str(out/'restored.png');cmd[cmd.index('--dump-scene')+1]=str(out/'restored.json')
with (out/'restored.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
image=lambda k:Image.open(out/k/'window.png').convert('RGB')
different=lambda a,b:ImageChops.difference(image(a),image(b)).getbbox() is not None
checks=dict(all_actual_healthy_scenes=all(c['level']==int(k[0]) and c['scene']['health']>0 for k,c in cases.items()),native_picture_preserved=not different('5-old','5-native'),hakuna_guest_state_preserved=len({(c['frame_sha256'],c['wram_sha256']) for k,c in cases.items() if k.startswith('5-')})==1,destiny_guest_state_preserved=cases['6-native']['wram_sha256']==cases['6-md']['wram_sha256'],background_visible=different('5-native','5-background'),palette_visible=different('5-native','5-palette'),independent_choices=different('5-background','5-md') and different('5-palette','5-md'),destiny_background_visible=different('6-native','6-md'),current_save_picture=digest(out/'restored.png')==digest(out/'5-md/window.png'),current_save_clock=json.loads((out/'restored.json').read_text())['hakuna_waterfall']==cases['5-md']['waterfall'])
paths=[Path(__file__),ROOT/'build/hakuna786/build-report.json',ROOT/'build/hakuna787-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,restore_command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
