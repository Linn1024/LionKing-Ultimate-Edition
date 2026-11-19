"""Direct Pride Rock start verifies unreviewed scenery stays native under MD selection."""
import json,os,subprocess,re
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later904-fallback';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/later885-choices/report.json').read_text())['cases']['8-native']['command'].copy();base[0]=str(ROOT/'build/later901/player.exe')
for flag in ('--load','--input-polled'):
 i=base.index(flag);del base[i:i+2]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={}
for name,profile in [('prepare',''),('native',''),('md-scenery','graphics.scenery = md\n')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();end=2400 if name=='prepare' else 2440
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+profile)
 if name=='prepare':cmd+=['--practice-level','9','--save-at','2400',str(out/'pride-rock.state')]
 else:cmd+=['--load',str(out/'pride-rock.native.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 if name=='prepare':native_fixture(out/'pride-rock.state',out/'pride-rock.native.state',2400)
 s=json.loads((folder/'scene.json').read_text());cases[name]=dict(command=cmd,window_sha256=digest(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),level=s['level'],gameplay=s['latched_gameplay'])
n=cases['native'];m=cases['md-scenery'];checks=dict(actual_scene9=all(c['level']==9 and c['gameplay']['health']>0 for c in cases.values()),native_fallback_picture=n['window_sha256']==m['window_sha256'],guest_preserved=n['guest']==m['guest']);paths=[Path(__file__),ROOT/'build/later901/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,scope='Scenery selection in unsupported9 uses native art and its live palette; decoded generic tiles do not enable the renderer. Shared independently selected body colors remain separate.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
