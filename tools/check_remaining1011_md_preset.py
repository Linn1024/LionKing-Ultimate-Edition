"""Select all available MD choices through the real resource editor for TAS checks."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
out=ROOT/'build/remaining1011-md-preset';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/bonus991-play/report.json').read_text())['cases']['view-10']['command'].copy()
for flag,n in (('--load',2),('--input-polled',2),('--dump-window',2)):
 if flag in cmd:i=cmd.index(flag);del cmd[i:i+n]
cmd[0]=str(ROOT/'build/remaining1006-player/player.exe')
for flag,value in (('--frames',5000),('--hash-at',2200),('--sprite-assets',ROOT/'build/remaining1007-helper/sprites.assets'),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--practice-level','0','--menu-at','1500','--menu-page','resources'];(out/'host.ini').write_text('opengl = 0\nscale = 2\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();snapshots={};hwnd=None
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 def wait(predicate):
  deadline=time.monotonic()+30
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and predicate(row):return row
   time.sleep(.005)
  raise AssertionError(('UI state',proc.poll(),trace.latest()))
 def key(vk):
  scan=USER32.MapVirtualKeyW(vk,0);USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16));USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16));time.sleep(.055)
 try:
  snapshots['initial']=wait(lambda r:r['about']==2 and r['field']==1500);hwnd=window_for(proc.pid);assert hwnd
  key(0x76);snapshots['draft']=wait(lambda r:r['modal'] and r['choices'][0][1]==2);capture_client(hwnd,out/'draft.png');key(0x1b);key(0x71)
  snapshots['after']=wait(lambda r:not r['menu'] and r['field']>=2100 and r['level']==0 and r['health']>0);capture_client(hwnd,out/'actual.png')
 finally:
  if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
  trace.finish()
choices={r[0]:r for r in snapshots['after']['choices']};checks=dict(clean_exit=proc.returncode==0,root_md=choices['game'][4]==2,scar_bounds_md=choices['gameplay.levels.pride_rock.scar_bounds'][4]==2,bonus_choices_md=all(choices[k][4]==2 for k in ('graphics.sprites.bonus.timon.frames','audio.music.bug_hunt')),unsupported_native=all(choices[k][4]==1 for k in ('gameplay.simba.movement','gameplay.simba.combat','audio.voices')),persisted=(out/'resources.ini').read_text().find('game = md')>=0)
paths=[Path(__file__),ROOT/'build/remaining1006-player/build-report.json',ROOT/'build/remaining1007-helper/build-report.json',out/'resources.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,snapshots=snapshots,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
