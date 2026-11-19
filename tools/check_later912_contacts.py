"""Exercise the real late-hyena body query with an independent gameplay choice."""
import json,os,subprocess,re,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/later912-contacts';out.mkdir(exist_ok=True);cases={};checks={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level in (7,8):
 for name,old,extra in [('old-native',True,''),('native',False,''),('md',False,'gameplay.levels.adult_hyenas.bounds = md\n')]:
  folder=out/f'{level}-{name}';folder.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later885-choices/report.json').read_text())['cases'][f'{level}-native']['command'].copy();cmd[0]=str(ROOT/('build/later901/player.exe' if old else 'build/later910/player.exe'))
  for flag,value in (('--sprite-assets',ROOT/('build/later882-helper/sprites.assets' if old else 'build/later909-helper/sprites.assets')),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
  (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+extra)
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_HITBOX_TRACE=str(folder/'bounds.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
  trace=list(csv.DictReader((folder/'bounds.csv').open())) if (folder/'bounds.csv').exists() else [];scene=json.loads((folder/'scene.json').read_text());cases[f'{level}-{name}']=dict(command=cmd,guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),picture=digest(folder/'window.png'),bounds_calls=len(trace),changed_edges=sum(r['native']!=r['md'] for r in trace),gameplay=scene['latched_gameplay']);print(level,name,len(trace),cases[f'{level}-{name}']['gameplay']['health'],flush=True)
 c={k:cases[f'{level}-{k}'] for k in ('old-native','native','md')};checks[f'{level}/native_preserved']=c['native']['guest']==c['old-native']['guest'] and c['native']['picture']==c['old-native']['picture'];checks[f'{level}/real_bounds_used']=c['md']['bounds_calls']>0 and c['md']['changed_edges']>0;checks[f'{level}/native_choice_untouched']=c['native']['bounds_calls']==0;checks[f'{level}/healthy']=c['md']['gameplay']['health']>0
paths=[Path(__file__),ROOT/'build/later910/build-report.json',ROOT/'build/later909-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
