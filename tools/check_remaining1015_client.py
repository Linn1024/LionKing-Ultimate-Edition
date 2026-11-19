"""Real full-available-MD Scar client and same-build save continuation."""
import csv,json,os,re,shutil,struct,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/remaining1015-client';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/remaining1009-scar/report.json').read_text())['cases']['md']['command'];cases={};USER32.SetProcessDPIAware()
for name in ('direct','restored'):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy()
 for flag,value in (('--frames',57200),('--hash-at',57200),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--input-polled',folder/'input.polled.tape')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');shutil.copy2(ROOT/'build/remaining1011-md-preset/resources.ini',folder/'resources.ini');pads=[0x4000 if (i//10)%2==0 else 0 for i in range(300)];(folder/'input.polled.tape').write_bytes(struct.pack('<300H',*pads))
 if name=='direct':cmd+=['--save-at','57100',str(folder/'current.state')]
 else:cmd[cmd.index('--load')+1]=str(out/'direct/current.state')
 trace=JsonPipe(folder/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_HITBOX_TRACE=str(folder/'bounds.csv'));captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+20
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=57130 and row['health']>0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:capture_client(hwnd,folder/'actual.png');captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 scene=json.loads((folder/'scene.json').read_text());rows=list(csv.DictReader((folder/'bounds.csv').open()));cases[name]=dict(command=cmd,clean_exit=proc.returncode==0,actual_field=captured and captured['field'],colors=len(Image.open(folder/'actual.png').getcolors(1000000) or []),gameplay=scene['latched_gameplay'],picture=digest(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),bounds_calls=len(rows));print(name,cases[name]['gameplay'],cases[name]['bounds_calls'],flush=True)
checks=dict(actual_md_combat=all(r['clean_exit'] and r['actual_field'] and r['colors']>16 and r['gameplay']['health']>0 and r['bounds_calls']>0 for r in cases.values()),current_save_picture=cases['direct']['picture']==cases['restored']['picture'],current_save_guest=cases['direct']['guest']==cases['restored']['guest'])
paths=[Path(__file__),ROOT/'build/remaining1014-player/build-report.json',ROOT/'build/remaining1011-md-preset/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
