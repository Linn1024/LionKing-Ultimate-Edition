"""Focused bonus client views, ordinary Hunt input and current-save continuation."""
import csv,json,os,re,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for

out=ROOT/'build/bonus991-play';out.mkdir(exist_ok=True)
refs=json.loads((ROOT/'build/bonus972-choices/report.json').read_text())['cases']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
cases={};checks={};USER32.SetProcessDPIAware()
def run(level,name,end,restore=None,pad=0,live=False,save=False):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=refs[f'{level}-both']['command'].copy();cmd[0]=str(ROOT/'build/bonus989/player.exe')
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--sprite-assets',ROOT/'build/bonus985-sprite-helper/sprites.assets'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 if restore:cmd[cmd.index('--load')+1]=str(restore)
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ngraphics.sprites.bonus = md\ngraphics.scenery = md\ndisplay.viewport = md\naudio.music.bug_toss = md\naudio.music.bug_hunt = md\n')
 (folder/'input.polled.tape').write_bytes(pad.to_bytes(2,'little')*7000);cmd+=['--input-polled',str(folder/'input.polled.tape')]
 if save:cmd+=['--save-at','2000',str(folder/'current.state')]
 trace=JsonPipe(folder/'tree.jsonl.gz');captured=None
 with (folder/'run.log').open('wb') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_BG_TRACE=str(folder/'scenes.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+50
   while proc.poll() is None and time.monotonic()<deadline:
    row=trace.latest()
    if live and row and row['level']==level and row['field']>=(1730 if level==10 else 1930) and captured is None:
     hwnd=window_for(proc.pid)
     if hwnd:capture_client(hwnd,folder/'actual.png');captured=row
    time.sleep(.005)
   proc.wait(timeout=5)
  finally:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   trace.finish()
 assert proc.returncode==0
 scene=json.loads((folder/'scene.json').read_text());r=dict(command=cmd,level=scene['level'],gameplay=scene['latched_gameplay'],window_sha256=digest(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),captured_field=captured and captured['field'])
 if live:r['actual_colors']=len(Image.open(folder/'actual.png').convert('RGB').getcolors(1000000) or [])
 cases[name]=r;print(name,r['level'],r['gameplay'],r.get('actual_colors'),flush=True);return r

for level in range(10,14):
 r=run(level,f'view-{level}',1800 if level==10 else 2020,live=True)
 checks[f'{level}/real_client']=r['captured_field'] is not None and r['actual_colors']>16
 checks[f'{level}/correct_level']=r['level']==level
a=run(13,'hunt-right',2100,pad=0x100,save=True)
b=run(13,'hunt-restored',2100,pad=0x100,restore=out/'hunt-right/current.state')
checks['current_save_picture']=a['window_sha256']==b['window_sha256']
checks['current_save_guest']=a['guest']==b['guest']
checks['ordinary_input_moves']=a['gameplay']['player']!=cases['view-13']['gameplay']['player']
paths=[Path(__file__),ROOT/'build/bonus989/build-report.json',ROOT/'build/bonus985-sprite-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
