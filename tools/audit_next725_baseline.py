"""Capture current fourth/fifth levels directly, retaining their real renderer evidence."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next725-baseline';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/graveyard660-skull-audio/report.json').read_text())['commands']['death'];cases={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in (3,4):
 for source in ('snes','md'):
  folder=out/f'{level}-{source}';folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'dist/installed-preview720/LionKing.exe')
  for flag,count in (('--wav',2),('--wav-seconds',2)):
   if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
  for flag,value in (('--practice-level',str(level)),('--frames','2300'),('--hash-at','2300'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard707-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
  (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
  (folder/'resources.ini').write_text(('schema = 1\ngame = snes\n' if source=='snes' else (ROOT/'profiles/graveyard-md.ini').read_text()))
  cmd+=['--save-at','2300',str(folder/'entry.state')]
  if not (folder/'scene.json').exists():
   with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
  scene=json.loads((folder/'scene.json').read_text());cases[f'{level}-{source}']=dict(command=cmd,level=scene['level'],stage=scene['stage_detected'],gameplay=scene['latched_gameplay']);print(level,source,scene['latched_gameplay'],flush=True)
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',cases=cases,source_sha256={str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))}),indent=2)+'\n')
