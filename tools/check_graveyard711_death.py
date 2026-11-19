"""Focused fresh health death, current save restore and retry presentation checks."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard711-death';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/graveyard660-skull-audio/report.json').read_text())['commands']['death']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
cases={}
for name,end,source,load in [('early',2100,'md',False),('middle',2140,'md',False),('native',2140,'snes',False),('restored',2140,'md',True),('retry',2600,'md',True)]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'build/graveyard708/player.exe')
 for flag,count in (('--wav',2),('--wav-seconds',2),('--save-at',3)):
  if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
 for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard707-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
 (folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\ngameplay.levels.elephant_graveyard = snes\ngraphics.sprites.simba.cub.graveyard_death_motion = '+source+'\n')
 if name=='early':cmd+=['--save-at','2100',str(out/'death.state')]
 if load:
  i=cmd.index('--practice-level');del cmd[i:i+2];cmd+=['--load',str(out/'death.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
 scene=json.loads((folder/'scene.json').read_text());cases[name]=dict(command=cmd,death=scene['graveyard_death'],gameplay=scene['latched_gameplay'],window_sha256=digest(folder/'window.png'))
 print(name,cases[name]['death'],cases[name]['gameplay'],flush=True)
checks=dict(active=cases['early']['death']['selected']==1,moves=cases['middle']['death']['age']>cases['early']['death']['age'],independent=cases['native']['death']['selected']==0 and cases['native']['window_sha256']!=cases['middle']['window_sha256'],save_restore=cases['middle']['window_sha256']==cases['restored']['window_sha256'],retry=cases['retry']['death']['selected']==0 and cases['retry']['gameplay']['health']>0)
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),ROOT/'build/graveyard708/build-report.json',ROOT/'build/graveyard707-helper/build-report.json')}),indent=2)+'\n')
print(checks)
