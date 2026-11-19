"""Exercise both delivered CMDs and inspect actual clients/applied choices."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
publication=ROOT/'build/later918-publication/report.json';bound(publication);out=ROOT/'build/later919-installed';out.mkdir(exist_ok=True);cases={};USER32.SetProcessDPIAware();ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
for level,name,settings,keys in [(7,'Play Be Prepared MD.cmd','be-prepared-md',('graphics.scenery.background','graphics.sprites.enemies.hyenas.adult.frames','graphics.sprites.enemies.hyenas.adult.palette','gameplay.levels.adult_hyenas.bounds','audio.effects.world.adult_hyenas.attack','audio.effects.world.adult_hyenas.reaction','audio.music.be_prepared.track','audio.music.be_prepared.death')),(8,'Play Simbas Return MD.cmd','return-md',('graphics.scenery.background','graphics.sprites.enemies.hyenas.adult.frames','graphics.sprites.enemies.hyenas.adult.palette','gameplay.levels.adult_hyenas.bounds','audio.effects.world.adult_hyenas.attack','audio.effects.world.adult_hyenas.reaction','audio.music.simbas_return.track','audio.music.simbas_return.death'))]:
 folder=out/settings;folder.mkdir(exist_ok=True);trace=JsonPipe(folder/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
 cmd=[os.environ['COMSPEC'],'/d','/c',str(ROOT/name),'-Frames','2400','-NoPace','-NoAudio','-WindowCapture',str(folder/'window.png'),'-SceneCapture',str(folder/'scene.json')];captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+50
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=1650 and row['level']==level and row['health']>0 and captured is None:
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
paths=[Path(__file__),publication,ROOT/'Play Be Prepared MD.cmd',ROOT/'Play Simbas Return MD.cmd',ROOT/'profiles/be-prepared-md.ini',ROOT/'profiles/return-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
