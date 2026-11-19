"""Capture actual healthy native Hakuna/Destiny clients from nearby checkpoints.

These establish the current player surface, not completion of mixed resources.
"""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna784-windows';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cases={}
base=json.loads((ROOT/'build/hakuna781-native/report.json').read_text())['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for frame,level,source in ((27000,5,ROOT/'build/hakuna778-checkpoint/entry.state'),(38000,6,ROOT/'build/hakuna781-native/38000.state')):
 folder=out/str(level);folder.mkdir(exist_ok=True);native_fixture(source,folder/'entry.native.state',frame)
 cmd=base.copy();cmd[0]=str(ROOT/'dist/installed-preview771/LionKing.exe')
 for flag,count in (('--input-polled',2),('--save-at',3)):
  while flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
 cmd.remove('--no-pace')
 for flag,value in (('--load',folder/'entry.native.state'),('--frames',frame+180),('--hash-at',frame+180),('--config',folder/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+15
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=frame+30 and row['level']==level and row['health']>0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:capture_client(hwnd,folder/'actual.png');captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 cases[str(level)]=dict(command=cmd,exit=proc.returncode,captured_field=captured and captured['field'],health=captured and captured['health'])
 print(level,cases[str(level)]['captured_field'],flush=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(c['exit']==0 and c['captured_field'] for c in cases.values()) else 'FAIL',scope=__doc__,cases=cases),indent=2)+'\n')
