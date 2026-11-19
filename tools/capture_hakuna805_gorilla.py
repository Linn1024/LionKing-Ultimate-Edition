"""Verify the actual Windows gorilla client using prepared artwork and palette."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/hakuna805-gorilla';out.mkdir(exist_ok=True);USER32.SetProcessDPIAware()
cmd=json.loads((ROOT/'build/hakuna803-gorilla/report.json').read_text())['cases']['both']['command'].copy();cmd.remove('--no-pace')
for flag,value in (('--frames',35240),('--hash-at',35240),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 2\n');trace=JsonPipe(out/'tree.jsonl.gz');captured=None;env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_REPORT=str(out/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+15
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and row['field']>=35080 and row['level']==5 and row['health']>0 and captured is None:
    hwnd=window_for(proc.pid)
    if hwnd:capture_client(hwnd,out/'actual.png');captured=row
   time.sleep(.005)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
last=trace.latest();choices={r[0]:r for r in last['choices']};sprites=json.loads((out/'sprites.json').read_text());checks=dict(actual_client=captured is not None,clean_exit=proc.returncode==0,gorilla_images_used=sprites['seen_by_role']['gorilla']>0,independent_md_choices=all(choices['graphics.sprites.enemies.gorilla.'+k][4]==2 for k in ('frames','palette')))
paths=[Path(__file__),ROOT/'build/hakuna802/build-report.json',ROOT/'build/hakuna801-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,captured_field=captured and captured['field'],seen_gorilla_frames=sprites['seen_by_role']['gorilla'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
