"""Final Stampede backdrop and actual-window check; no unrelated level replay."""
import json,os,subprocess,time
from PIL import Image
from audit_scenes import ROOT
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/next767-backdrop';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/next761-windows/report.json').read_text())['cases']['stampede']['command'].copy();cmd[0]=str(ROOT/'build/next766/player.exe')
for flag,value in (('--frames','2335'),('--hash-at','2335'),('--config',str(out/'host.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();captured=False
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+15
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and row['field']>=2310 and not captured:
    hwnd=window_for(proc.pid)
    if hwnd:capture_client(hwnd,out/'actual.png');captured=True
   time.sleep(.004)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
im=Image.open(out/'window.png').convert('RGB');color=im.getpixel((im.width//2,1));checks=dict(actual_window=captured,clean_exit=proc.returncode==0,original_md_black_backdrop=color==(0,0,0))
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,backdrop_rgb=color,command=cmd),indent=2)+'\n');print(checks,color)
