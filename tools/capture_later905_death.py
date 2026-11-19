"""Actual7/8 death clients and one current audio/death save with restored picture."""
import json,os,subprocess,time,re
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/later905-death';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in (7,8):
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later899-audio/report.json').read_text())['cases'][f'{level}-death-md']['command'].copy();cmd[0]=str(ROOT/'build/later901/player.exe');cmd.remove('--no-pace');start=json.loads((ROOT/'build/later898-deaths/report.json').read_text())['cases'][str(level)]['frame']
 for flag in ('--wav','--wav-seconds'):
  i=cmd.index(flag);del cmd[i:i+2]
 for flag,value in (('--frames',start+220),('--hash-at',start+220),('--config',folder/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
 if level==8:cmd+=['--save-at',str(start+140),str(out/'current-death.state')]
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
      capture_client(hwnd,folder/'actual.png');colors=Image.open(folder/'actual.png').convert('RGB').getcolors(65536)
      if colors is None or len(colors)>3:captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 checks=dict(actual_visible_death=captured is not None,clean_exit=proc.returncode==0);cases[str(level)]=dict(checks=checks,command=cmd,captured_field=captured and captured['field']);print(level,checks,flush=True)
# Restore only the changed current audio/death continuation; no old-save matrix.
folder=out/'restored';folder.mkdir(exist_ok=True);cmd=cases['8']['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--load',out/'current-death.state'),('--config',folder/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(folder/'host.ini').write_text('opengl = 0\nscale = 3\n');cmd+=['--no-pace']
with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
checks=dict(actual_deaths=all(all(c['checks'].values()) for c in cases.values()),current_save_picture=digest(folder/'window.png')==digest(out/'8/window.png'));paths=[Path(__file__),ROOT/'build/later901/build-report.json',ROOT/'build/later899-audio/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,restore_command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
