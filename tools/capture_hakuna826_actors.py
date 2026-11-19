"""Actual actor clients using the final reviewed repertoire and source controls."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna826-actors';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,level,reference,threshold,end in [('frogs-spiders',5,'build/hakuna817-opening/report.json',27680,27850),('destiny-actors',6,'build/hakuna816-actors/report.json',38030,38180)]:
 folder=out/name;folder.mkdir(exist_ok=True);r=json.loads((ROOT/reference).read_text());cmd=(r['command'] if level==5 else r['cases']['6-both']['command']).copy();cmd[0]=str(ROOT/'build/hakuna823/player.exe')
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
 if level==6:
  i=cmd.index('--input-polled');del cmd[i:i+2];cmd[cmd.index('--load')+1]=str(ROOT/'build/hakuna796-simba/6.native.state');cmd.remove('--no-pace')
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+30
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=threshold and row['level']==level and row['health']>0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:
      capture_client(hwnd,folder/'actual.png')
      if len(Image.open(folder/'actual.png').convert('RGB').getcolors(65536) or [0]*65537)>16:captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 sp=json.loads((folder/'sprites.json').read_text());checks=dict(actual_visible_client=captured is not None,clean_exit=proc.returncode==0,owned_actor_images_used=sp['later_roles']['enemies']>0)
 if level==6:checks.update(world_objects=sp['later_roles']['world']>0)
 cases[name]=dict(command=cmd,checks=checks,captured_field=captured and captured['field'],roles=sp['later_roles']);print(name,checks,flush=True)
paths=[Path(__file__),ROOT/'build/hakuna823/build-report.json',ROOT/'build/hakuna822-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
