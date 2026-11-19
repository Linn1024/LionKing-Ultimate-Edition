"""Real final-build Stampede/death clients and a current-build death save restore."""
import json,os,subprocess,time,re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/next761-windows';out.mkdir(exist_ok=True);env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware();cases={}
templates=[('stampede',json.loads((ROOT/'build/next745-presentation/report.json').read_text())['cases']['3-md']['command'],2370,(2320,)),('exile-death',json.loads((ROOT/'build/next757-death/report.json').read_text())['cases']['restored']['command'],25640,(25566,25610))]
for name,base,end,fields in templates:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'build/next763/player.exe')
 for flag,count in (('--wav',2),('--wav-seconds',2)):
  if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
 cmd.remove('--no-pace')
 for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--config',str(folder/'host.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
 if name=='exile-death':cmd[cmd.index('--load')+1]=str(ROOT/'build/next757-death/death.native.state');cmd+=['--save-at','25575',str(out/'current-death.state')]
 trace=JsonPipe(folder/'tree.jsonl.gz');captured=[]
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+15
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and len(captured)<len(fields) and row['field']>=fields[len(captured)]:
     hwnd=window_for(proc.pid)
     if hwnd:capture_client(hwnd,folder/f'actual-{len(captured)}.png');captured.append(row['field'])
    time.sleep(.004)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 cases[name]=dict(command=cmd,captured=captured,exit=proc.returncode);print(name,captured,flush=True)
base=cases['exile-death']['command'];cmd=base.copy();cmd+=['--no-pace'];i=cmd.index('--save-at');del cmd[i:i+3]
cmd[cmd.index('--load')+1]=str(out/'current-death.state');cmd[cmd.index('--dump-window')+1]=str(out/'restored.png');cmd[cmd.index('--dump-scene')+1]=str(out/'restored.json')
with (out/'restored.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
checks=dict(stampede_actual_window=len(cases['stampede']['captured'])==1,death_actual_movement_windows=len(cases['exile-death']['captured'])==2,current_build_save=digest(out/'restored.png')==digest(out/'exile-death/window.png'))
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,restore_command=cmd),indent=2)+'\n');print(checks)
