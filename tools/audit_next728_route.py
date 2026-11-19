"""Inventory actual Stampede/Exile actors on the existing level-only continuation."""
import json,os,subprocess,time,csv,collections
from audit_scenes import ROOT
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/next729-route';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/graveyard516-route/report.json').read_text())['command'];cmd=base.copy();cmd[0]=str(ROOT/'build/next727-observer/player.exe')
for flag,count in (('--wav',2),('--wav-seconds',2),('--save-at',3)):
 if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
for flag,value in (('--frames','27000'),('--hash-at','22000,25000,27000'),('--load',str(ROOT/'build/graveyard516-route/endpoint.state')),('--input-polled',str(out/'continuation.polled.tape')),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard707-helper/sprites.assets')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'continuation.polled.tape').write_bytes((ROOT/'build/graveyard516-route/graveyard.polled.tape').read_bytes()[6036*2:])
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text())
cmd+=['--save-at','24500',str(out/'exile.state')]
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_OBJECTS=str(out/'poses.csv'),TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'))
USER32.SetProcessDPIAware();captures={};last=None
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+100
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row:
    last=row
    for label,level,field in (('stampede',3,20500),('stampede-late',3,22000),('exile',4,24500),('exile-late',4,25500)):
     if row['level']==level and field<=row['field']<field+200 and label not in captures:
      hwnd=window_for(proc.pid)
      if hwnd:capture_client(hwnd,out/(label+'.png'));captures[label]=row
   time.sleep(.008)
  proc.wait(timeout=10)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
groups=collections.defaultdict(list)
for row in csv.DictReader((out/'poses.csv').open()):groups[row['descriptor']].append(row)
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd,captures=captures,last=last,descriptors={k:len(v) for k,v in groups.items()}),indent=2)+'\n');print('route',proc.returncode,last and (last['field'],last['level'],last['health']),{k:len(v) for k,v in groups.items()})
