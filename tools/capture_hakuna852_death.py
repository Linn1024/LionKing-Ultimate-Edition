"""Actual Windows health-death clients at nearby prepared native checkpoints."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna852-death';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start,fixture,source in [(5,36430,'build/hakuna844-deaths/5/before.native.state','hakuna_matata'),(6,38641,'build/hakuna845-adult/before.native.state','simbas_destiny')]:
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/hakuna846-music/report.json').read_text())['cases'][f'{level}-md']['command'].copy();cmd[0]=str(ROOT/'build/hakuna849/player.exe');cmd.remove('--no-pace')
 for flag in ('--wav','--wav-seconds'):
  i=cmd.index(flag);del cmd[i:i+2]
 for flag,value in (('--frames',start+220),('--hash-at',start+220),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text(f'schema = 1\ngame = snes\naudio.music.{source} = md\n'+('graphics.sprites.simba.cub.hakuna_death_motion = md\ngraphics.sprites.simba.cub.frames = md\ngraphics.sprites.simba.cub.palette = md\n' if level==5 else ''))
 trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+15
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=start+130 and row['level']==level and row['health']==0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:
      capture_client(hwnd,folder/'actual.png')
      colors=Image.open(folder/'actual.png').convert('RGB').getcolors(65536)
      if (colors is None or len(colors)>3) and Image.open(folder/'actual.png').getbbox():captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 checks=dict(actual_visible_death=captured is not None,clean_exit=proc.returncode==0);cases[str(level)]=dict(checks=checks,command=cmd,captured_field=captured and captured['field']);print(level,checks,flush=True)
paths=[Path(__file__),ROOT/'build/hakuna849/build-report.json',ROOT/'build/hakuna846-music/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'INCOMPLETE',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
