"""Actual Windows Be Prepared background using imported data and direct saved start."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/be-prepared869-windows';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cmd=json.loads((ROOT/'build/be-prepared868-choices/report.json').read_text())['cases']['both']['command'].copy();cmd.remove('--no-pace');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--frames',44680),('--hash-at',44680),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\ngraphics.scenery.background = md\ngraphics.scenery.palettes = md\ndisplay.viewport = md\n');trace=JsonPipe(out/'tree.jsonl.gz');captured=None;env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+15
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and row['field']>=44560 and row['level']==7 and row['health']>0 and captured is None:
    hwnd=window_for(proc.pid)
    if hwnd:
     capture_client(hwnd,out/'actual.png');colors=Image.open(out/'actual.png').convert('RGB').getcolors(65536)
     if colors is None or len(colors)>16:captured=row
   time.sleep(.005)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
checks=dict(actual_visible_client=captured is not None,correct_width=captured is not None and captured['width']==320,clean_exit=proc.returncode==0);paths=[Path(__file__),ROOT/'build/be-prepared866/build-report.json',ROOT/'build/be-prepared868-choices/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,captured_field=captured and captured['field'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
