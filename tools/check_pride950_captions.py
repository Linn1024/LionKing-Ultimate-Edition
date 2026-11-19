"""Adult opening captions stay centered; guest state and actual Windows clients checked."""
import json,os,re,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/pride950-captions';out.mkdir(exist_ok=True);env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={};checks={};USER32.SetProcessDPIAware();base=json.loads((ROOT/'build/pride931-choices/report.json').read_text())['cases']['9-both']['command'].copy()
for flag in ('--load','--input-polled'):
 i=base.index(flag);del base[i:i+2]
def centre(path):
 im=Image.open(path).convert('RGB');scale=im.width/320;pts=[(x,y) for y in range(int(30*scale),int(100*scale)) for x in range(im.width) if (lambda c:c[0]>180 and c[1]>120 and c[2]<120)(im.getpixel((x,y)))];assert pts,path;return (min(x for x,y in pts)+max(x for x,y in pts)+1)/2/scale
for level in (7,9):
 for name in ('old','new'):
  folder=out/f'{level}-{name}';folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/f'build/pride{943 if name=="old" else 949}/player.exe');cmd+=['--practice-level',str(level)]
  for flag,value in (('--frames',1750),('--hash-at',1750),('--config',folder/'host.ini'),('--resource-profile',ROOT/'profiles/pride-rock-md.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
  (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'run.log').write_text('')
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
  cases[f'{level}-{name}']=dict(command=cmd,centre=centre(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)));print(level,name,cases[f'{level}-{name}']['centre'],flush=True)
 n=cases[f'{level}-new'];o=cases[f'{level}-old'];checks[f'{level}/centered']=abs(n['centre']-160)<=3;checks[f'{level}/guest_preserved']=n['guest']==o['guest'];checks[f'{level}/visible_correction']=abs(o['centre']-160)>20
 folder=out/f'{level}-live';folder.mkdir(exist_ok=True);cmd=n['command'].copy();cmd[cmd.index('--frames')+1]='2400';cmd[cmd.index('--config')+1]=str(folder/'host.ini');cmd[cmd.index('--dump-window')+1]=str(folder/'window.png');cmd[cmd.index('--dump-scene')+1]=str(folder/'scene.json');(folder/'host.ini').write_text('opengl = 0\nscale = 3\n');trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  p=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+25
   while p.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=1700 and row['field']<1780 and captured is None:
     hwnd=window_for(p.pid)
     if hwnd:capture_client(hwnd,folder/'actual.png');captured=row
    time.sleep(.003)
   p.wait(timeout=5)
  finally:
   if p.poll() is None:p.terminate();p.wait(timeout=5)
   trace.finish()
 checks[f'{level}/actual_client']=captured is not None and p.returncode==0;cases[f'{level}-live']=dict(command=cmd,captured=captured and captured['field']);print('actual',level,captured and captured['field'],flush=True)
paths=[Path(__file__),ROOT/'build/pride949/build-report.json',ROOT/'build/pride943/build-report.json'];(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
