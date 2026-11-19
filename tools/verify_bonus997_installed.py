"""Exercise both delivered CMDs and inspect actual clients/applied choices."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
publication=ROOT/'build/bonus996-publication/report.json';bound(publication);out=ROOT/'build/bonus997-installed';out.mkdir(exist_ok=True);cases={};USER32.SetProcessDPIAware();ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
for level,name,settings,keys in [(10,'Play Bug Toss MD.cmd','bug-toss-md',('graphics.sprites.bonus.pumbaa.frames','graphics.sprites.bonus.timon.palette','audio.music.bug_toss')),(11,'Play Bug Hunt 1 MD.cmd','bug-hunt-1-md',('graphics.sprites.bonus.timon.frames','graphics.sprites.bonus.bugs.palette','audio.music.bug_hunt')),(12,'Play Bug Hunt 2 MD.cmd','bug-hunt-2-md',('graphics.sprites.bonus.timon.frames','graphics.sprites.bonus.bugs.palette','audio.music.bug_hunt')),(13,'Play Bug Hunt 3 MD.cmd','bug-hunt-3-md',('graphics.sprites.bonus.timon.frames','graphics.sprites.bonus.bugs.palette','audio.music.bug_hunt'))]:
 folder=out/settings;folder.mkdir(exist_ok=True);trace=JsonPipe(folder/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
 cmd=[os.environ['COMSPEC'],'/d','/c',str(ROOT/name),'-Frames',str(1800 if level==10 else 2050),'-NoPace','-NoAudio','-WindowCapture',str(folder/'window.png'),'-SceneCapture',str(folder/'scene.json')];captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+50
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=(1730 if level==10 else 1930) and row['level']==level and row['health']>0 and captured is None:
     query="Get-CimInstance Win32_Process -Filter \"Name='LionKing.exe'\" | Where-Object { $_.CommandLine -like '*settings\\"+settings+"*' } | Select-Object -ExpandProperty ProcessId"
     pids=subprocess.check_output([ps,'-NoProfile','-Command',query],creationflags=subprocess.CREATE_NO_WINDOW,text=True)
     for pid in pids.split():
      hwnd=window_for(int(pid))
      if hwnd:capture_client(hwnd,folder/'actual.png');captured=row;break
    time.sleep(.008)
   proc.wait(timeout=10)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 last=trace.latest();choices={x[0]:x for x in last['choices']};scene=json.loads((folder/'scene.json').read_text());checks=dict(clean_cmd=proc.returncode==0,actual_live_client=captured is not None,correct_level=scene['level']==level,correct_viewport=last['width']==320,new_md_choices=all(choices[k][4]==2 for k in keys),separate_settings=(ROOT/f'settings/{settings}/resources.ini').exists())
 cases[settings]=dict(command=cmd,checks=checks,captured_field=captured and captured['field']);print(settings,checks,flush=True)
paths=[Path(__file__),publication]+[ROOT/('Play '+name+' MD.cmd') for name in ('Bug Toss','Bug Hunt 1','Bug Hunt 2','Bug Hunt 3')]+[ROOT/('profiles/'+key+'.ini') for key in ('bug-toss-md','bug-hunt-1-md','bug-hunt-2-md','bug-hunt-3-md')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
