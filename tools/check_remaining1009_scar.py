"""Actual Scar rectangle queries, native control and ordinary final encounter route."""
import csv,json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1009-scar';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/pride933-route/report.json').read_text())['command'].copy()
if '--save-at' in base:i=base.index('--save-at');del base[i:i+3]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={};checks={}
for name,old,md in [('old-native',True,False),('native',False,False),('md',False,True)]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('dist/installed-preview989/LionKing.exe' if old else 'build/remaining1006-player/player.exe'))
 for flag,value in (('--frames',57500),('--hash-at',57500),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--sprite-assets',ROOT/('build/bonus985-sprite-helper/sprites.assets' if old else 'build/remaining1007-helper/sprites.assets')),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+('gameplay.levels.pride_rock.scar_bounds = md\n' if md else ''))
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_HITBOX_TRACE=str(folder/'bounds.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 rows=list(csv.DictReader((folder/'bounds.csv').open())) if (folder/'bounds.csv').exists() else [];scene=json.loads((folder/'scene.json').read_text());cases[name]=dict(command=cmd,guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),picture=digest(folder/'window.png'),bounds_calls=len(rows),changed_edges=sum(r['native']!=r['md'] for r in rows),gameplay=scene['latched_gameplay']);print(name,cases[name]['bounds_calls'],cases[name]['changed_edges'],scene['latched_gameplay'],flush=True)
checks=dict(native_control_unchanged=cases['native']['guest']==cases['old-native']['guest'] and cases['native']['picture']==cases['old-native']['picture'],real_scar_queries=cases['md']['bounds_calls']>0 and cases['md']['changed_edges']>0,native_choice_untouched=cases['native']['bounds_calls']==0,healthy=cases['md']['gameplay']['health']>0)
paths=[Path(__file__),ROOT/'build/remaining1006-player/build-report.json',ROOT/'build/remaining1007-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
