"""Actual Simba clients, including an adult-art-only native256 direct start."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna797-simba';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware();cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
base=json.loads((ROOT/'build/hakuna796-simba/report.json').read_text())['cases']['5-frames']['command']
for name,level in (('cub',5),('adult-only',6)):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy()
 for flag,value in (('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
 if name=='cub':
  (folder/'resources.ini').write_bytes((ROOT/'build/hakuna796-simba/5-both/resources.ini').read_bytes());cmd.remove('--no-pace');end=31180;threshold=31025
 else:
  i=cmd.index('--load');del cmd[i:i+2];cmd+=['--practice-level','6'];end=2400;threshold=1600
  (folder/'resources.ini').write_text('schema = 1\ngame = snes\ngraphics.sprites.simba.adult.frames = md\n')
 for flag in ('--frames','--hash-at'):cmd[cmd.index(flag)+1]=str(end)
 trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+40
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=threshold and row['level']==level and row['health']>0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:capture_client(hwnd,folder/'actual.png');captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 s=json.loads((folder/'scene.json').read_text());sprites=json.loads((folder/'sprites.json').read_text());last=trace.latest();choices={r[0]:r for r in last['choices']};md=[k for k,r in choices.items() if r[4]==2]
 checks=dict(actual_client=captured is not None,clean_exit=proc.returncode==0,correct_healthy_scene=s['level']==level and s['latched_gameplay']['health']>0,prepared_images_used=sprites['seen_mapped_frames']>0)
 if name=='adult-only':checks.update(native256=last['width']==256,only_adult_art_md=md==['graphics.sprites.simba.adult.frames'])
 cases[name]=dict(command=cmd,checks=checks,captured_field=captured and captured['field'],seen_mapped_frames=sprites['seen_mapped_frames']);print(name,checks,flush=True)
paths=[Path(__file__),ROOT/'build/hakuna795/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
