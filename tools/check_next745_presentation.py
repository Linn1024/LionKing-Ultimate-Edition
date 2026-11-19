"""Short affected-scene controls: native and independently selected MD presentation."""
import json,os,subprocess,re
from audit_scenes import ROOT
out=ROOT/'build/next745-presentation';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/next725-baseline/report.json').read_text())['cases'];cases={}
choices=['graphics.sprites.simba.cub.frames','graphics.sprites.simba.cub.palette','graphics.sprites.enemies.other.frames','graphics.sprites.enemies.other.palette','graphics.sprites.leaves.frames','graphics.sprites.leaves.palette','graphics.scenery.foreground','graphics.scenery.background','graphics.scenery.palettes','graphics.scenery.stampede_palette','graphics.sprites.stampede.wildebeests.palette','graphics.sprites.stampede.rocks.frames','graphics.sprites.stampede.rocks.palette','graphics.hud.frames.roar','graphics.hud.frames.health','graphics.hud.frames.lives','graphics.hud.palette']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in (3,4):
 for source in ('native','md'):
  folder=out/f'{level}-{source}';folder.mkdir(exist_ok=True);cmd=base[f'{level}-snes']['command'].copy();cmd[0]=str(ROOT/'build/next743/player.exe')
  for flag,count in (('--practice-level',2),('--save-at',3)):
   if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
  for flag,value in (('--frames','2330'),('--hash-at','2330'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/next741-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
  cmd+=['--load',str(ROOT/f'build/next725-baseline/{level}-snes/entry.state')]
  (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+(''.join(k+' = md\n' for k in choices) if source=='md' else ''))
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
  scene=json.loads((folder/'scene.json').read_text());hashes=re.findall(r'wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text());cases[f'{level}-{source}']=dict(command=cmd,hash=hashes[-1],scene=scene['latched_gameplay']);print(level,source,scene['latched_gameplay'],flush=True)
checks={f'{level}_presentation_guest_unchanged':cases[f'{level}-native']['hash']==cases[f'{level}-md']['hash'] for level in (3,4)}
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases),indent=2)+'\n');print(checks)
