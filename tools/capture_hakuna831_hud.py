"""Actual adult MD life portrait, using the unchanged installed HUD data."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna831-hud';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cmd=json.loads((ROOT/'build/hakuna830-hud/report.json').read_text())['cases']['all-hud']['command'].copy();cmd.remove('--no-pace')
for flag,value in (('--frames',38200),('--hash-at',38200),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 2\n');trace=JsonPipe(out/'tree.jsonl.gz');captured=None;env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+15
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and row['field']>=38040 and row['level']==6 and row['health']>0 and captured is None:
    hwnd=window_for(proc.pid)
    if hwnd:
     capture_client(hwnd,out/'actual.png')
     if len(Image.open(out/'actual.png').convert('RGB').getcolors(65536) or [0]*65537)>16:captured=row
   time.sleep(.005)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
checks=dict(actual_visible_adult_client=captured is not None,clean_exit=proc.returncode==0)
paths=[Path(__file__),ROOT/'build/hakuna829/build-report.json',ROOT/'build/hakuna830-hud/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,captured_field=captured and captured['field'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
