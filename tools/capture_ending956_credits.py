"""Actual Windows adult-hyena clients and the independently selected late resources."""
import json,os,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/ending956-credits';out.mkdir(exist_ok=True);cases={};USER32.SetProcessDPIAware();env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start,threshold in [(9,70000,70030)]:
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/pride931-choices/report.json').read_text())['cases'][f'{level}-both']['command'].copy();cmd[0]=str(ROOT/'dist/installed-preview949/LionKing.exe');cmd.remove('--no-pace');cmd[cmd.index('--load')+1]=str(ROOT/'build/ending955-route/ending.native.state');i=cmd.index('--input-polled');del cmd[i:i+2]
 for flag,value in (('--frames',start+250),('--hash-at',start+250),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.sprites.simba.adult = md\ngraphics.sprites.enemies.scar = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.world_objects = md\ngraphics.sprites.pickups = md\ngraphics.hud.frames = md\n'+('graphics.scenery.background = md\ngraphics.scenery.palettes = md\n' if level==9 else ''))
 trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+15
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if row and row['field']>=threshold and row['level']==level and row['health']>0 and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:
      capture_client(hwnd,folder/'actual.png');colors=Image.open(folder/'actual.png').convert('RGB').getcolors(65536)
      if colors is None or len(colors)>16:captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 sp=json.loads((folder/'sprites.json').read_text());adult_seen=sp['seen_mapped_frames']-sum(sp['seen_by_role'].values())-sum(sp['later_roles'].values());checks=dict(actual_visible_client=captured is not None,correct_width=captured is not None and captured['width']==320,native_credits=json.loads((folder/'scene.json').read_text())['latched_gameplay']['descriptor']==0x83f,clean_exit=proc.returncode==0);cases[str(level)]=dict(checks=checks,command=cmd,captured_field=captured and captured['field'],adult_hyena_poses=adult_seen);print(level,checks,adult_seen,flush=True)
paths=[Path(__file__),ROOT/'build/pride949/build-report.json',ROOT/'build/pride931-choices/report.json',ROOT/'build/pride928-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(all(c['checks'].values()) for c in cases.values()) else 'INCOMPLETE',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
