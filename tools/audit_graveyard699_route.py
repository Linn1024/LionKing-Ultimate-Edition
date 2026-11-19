"""Whole-level current renderer coverage and Windows captures, using the existing level-only route."""
import json,os,csv,subprocess,time,collections
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference);observer=ROOT/'build/graveyard697-observer/report.json';bound(observer)
out=ROOT/'build/graveyard699-route';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(observer.parent/'player.exe')
for flag,count in (('--save-at',3),('--wav',2),('--wav-seconds',2)):
 if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
for flag,value in (('--frames','19500'),('--hash-at','13500,15500,18000,19500'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard683-helper/sprites.assets')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\ngameplay.levels.elephant_graveyard = snes\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_OBJECTS=str(out/'poses.csv'),TLK_SPRITE_REPORT=str(out/'sprites.json'))
USER32.SetProcessDPIAware();captures={};last=None
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+120
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row:
    last=row
    for label,field in (('opening',13500),('bones',14400),('flight',15500),('pillar',16500),('final-fight',18000)):
     if row['level']==2 and field<=row['field']<field+150 and label not in captures:
      hwnd=window_for(proc.pid)
      if hwnd:capture_client(hwnd,out/(label+'-client.png'));captures[label]=row
   time.sleep(.008)
  proc.wait(timeout=10)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
poses=list(csv.DictReader((out/'poses.csv').open()));groups=collections.defaultdict(list)
for row in poses:groups[row['descriptor']].append(row)
unmapped=[x for x in poses if x['palette'] in ('5','6') and x['mapped_role']=='0']
paths=[Path(__file__),reference,observer,ROOT/'profiles/graveyard-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED' if proc.returncode==0 else 'FAILED',command=cmd,last=last,captures=captures,unique_pose_count=len(poses),descriptors={k:len(v) for k,v in groups.items()},unmapped_bank5_6=unmapped,scope='Renderer/actor coverage along existing native-gameplay level route with all MD graphics/audio. Gameplay GY branch explicitly SNES to preserve this tape; not a completed MD-gameplay route. Private read-only observer; no maintained engine/runtime/installed changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('CURRENT',proc.returncode,'last',last and (last['field'],last['level'],last['health']),'descriptors',{k:len(v) for k,v in groups.items()},'unmapped',len(unmapped),flush=True)
