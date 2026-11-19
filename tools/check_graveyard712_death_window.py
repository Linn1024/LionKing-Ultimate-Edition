"""Inspect the moving Graveyard death in the real Windows client."""
import json,os,subprocess,time
from audit_scenes import ROOT
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/graveyard712-death-window';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/graveyard660-skull-audio/report.json').read_text())['commands']['death'];cmd=base.copy();cmd[0]=str(ROOT/'build/graveyard708/player.exe')
for flag,count in (('--wav',2),('--wav-seconds',2),('--practice-level',2)):
 if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
cmd.remove('--no-pace');cmd+=['--load',str(ROOT/'build/graveyard711-death/death.state')]
for flag,value in (('--frames','2170'),('--hash-at','2170'),('--config',str(ROOT/'build/graveyard711-death/early/host.ini')),('--resource-profile',str(ROOT/'build/graveyard711-death/early/resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard707-helper/sprites.assets')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();captured=[]
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+15
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and len(captured)<2 and row['field']>=(2113,2150)[len(captured)]:
    hwnd=window_for(proc.pid)
    if hwnd:
     capture_client(hwnd,out/f'actual-{len(captured)}.png');captured.append(row['field'])
   time.sleep(.004)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
(out/'report.json').write_text(json.dumps(dict(result='PASS' if len(captured)==2 and proc.returncode==0 else 'FAIL',captured_fields=captured,command=cmd),indent=2)+'\n');print(captured,proc.returncode)
