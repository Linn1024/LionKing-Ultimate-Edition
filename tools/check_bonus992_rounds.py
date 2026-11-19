"""Direct bonus round exits and real Hunt pickup effects under selected MD music."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus992-rounds';out.mkdir(exist_ok=True);refs=json.loads((ROOT/'build/bonus991-play/report.json').read_text())['cases'];cases={};checks={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in range(10,14):
 folder=out/str(level);folder.mkdir(exist_ok=True);cmd=refs[f'view-{level}']['command'].copy()
 for flag,value in (('--frames',6500),('--hash-at',6500),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ngraphics.sprites.bonus = md\ngraphics.scenery = md\ndisplay.viewport = md\naudio.music.bug_toss = md\naudio.music.bug_hunt = md\n')
 if level==13:
  cmd[cmd.index('--input-polled')+1]=str(ROOT/'build/bonus991-play/hunt-right/input.polled.tape');cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','6']
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_BG_TRACE=str(folder/'scenes.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'scenes.csv').open()));levels=[]
 for r in rows:
  n=int(r['level'])
  if not levels or levels[-1]!=n:levels.append(n)
 scene=json.loads((folder/'scene.json').read_text());cases[str(level)]=dict(command=cmd,levels=levels,final_gameplay=scene['latched_gameplay']);checks[f'{level}/round_exits']=levels[0]==level and any(n!=level for n in levels[1:]);print(level,levels,flush=True)
 if level==13:
  events=list(csv.DictReader((folder/'events.csv').open()));hits=[int(r['frame']) for r in events if r['event']=='0005' and r['parameter']=='0078' and int(r['frame'])<2100];stems=list(csv.DictReader((folder/'stems.csv').open()));near=[r for r in stems if any(f<=int(r['frame'])<f+15 for f in hits)]
  checks['hunt/ordinary_catches']=len(hits)>=1;checks['hunt/native_fx_with_md_music']=any(int(r['native_peak'])>0 and int(r['md_peak'])>0 for r in near);cases['13']['catch_fields']=hits;cases['13']['native_fx_peak']=max((int(r['native_peak']) for r in near),default=0)
paths=[Path(__file__),ROOT/'build/bonus991-play/report.json',ROOT/'build/bonus989/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
