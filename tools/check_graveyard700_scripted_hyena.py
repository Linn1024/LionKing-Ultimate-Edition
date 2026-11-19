"""Confirm the missed scripted hyena owner in current public684, through actual Windows capture."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/graveyard700-scripted-hyena';out.mkdir(exist_ok=True)
ref=ROOT/'build/graveyard626-choices/report.json';r=json.loads(ref.read_text());base=r['commands']['native'].copy();commands={};windows={};scenes={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name in ('md','snes','window'):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'dist/installed-preview684/LionKing.exe')
 for flag,count in (('--save-at',3),('--wav',2),('--wav-seconds',2)):
  if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
 for flag,value in (('--frames','17250' if name!='window' else '17295'),('--hash-at','17250' if name!='window' else '17295'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard683-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\ngameplay.levels.elephant_graveyard = snes\ngraphics.sprites.enemies.hyenas.frames = '+('snes' if name=='snes' else 'md')+'\ngraphics.sprites.enemies.hyenas.palette = '+('snes' if name=='snes' else 'md')+'\n')
 if name=='md':cmd+=['--save-at','17250',str(out/'observed.state')]
 if name=='window':
  cmd[cmd.index('--load')+1]=str(out/'observed.state');cmd.remove('--no-pace');trace=JsonPipe(folder/'tree.jsonl.gz');runenv=dict(env,TLK_SOFT_TREE_LOG=trace.name);captured=False;USER32.SetProcessDPIAware()
 else:runenv=env
 with (folder/'run.log').open('wb') as log:
  if name!='window':subprocess.run(cmd,cwd=ROOT,env=runenv,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
  else:
   proc=subprocess.Popen(cmd,cwd=ROOT,env=runenv,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   try:
    deadline=time.monotonic()+15
    while proc.poll() is None and time.monotonic()<deadline:
     row=trace.latest()
     if row and row['field']>=17251 and not captured:
      hwnd=window_for(proc.pid)
      if hwnd:capture_client(hwnd,folder/'actual-client.png');captured=True
     time.sleep(.004)
    proc.wait(timeout=5)
   finally:
    if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    trace.finish()
 commands[name]=cmd;windows[name]=Image.open(folder/'window.png').convert('RGB');scenes[name]=json.loads((folder/'scene.json').read_text());print(name,'done',flush=True)
pieces=[p for p in scenes['md']['pieces'] if p['actor_descriptor']==0xc58c80]
checks=dict(scripted_hyena_visible=bool(pieces),normal_native_palette=all(p['palette']==6 for p in pieces),md_choices_leave_picture_native=ImageChops.difference(windows['md'],windows['snes']).getbbox() is None,actual_windows_capture=captured)
paths=[Path(__file__),ref,ROOT/'engine/runner/tlk_wide.c',ROOT/'engine/runner/tlk_hyena_audio.c',ROOT/'engine/runner/tlk_graveyard_gameplay.c']
(out/'report.json').write_text(json.dumps(dict(result='GAP_CONFIRMED' if all(checks.values()) else 'CHECK_FAILED',checks=checks,commands=commands,pieces=pieces,scope='C58C80 scripted hyena in late Graveyard has mapped poses but current owner guards reject it. All-MD versus SNES hyena art/colors leave this entire picture identical. Uses original native gameplay route solely for encounter placement, not full MD-gameplay completion.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
