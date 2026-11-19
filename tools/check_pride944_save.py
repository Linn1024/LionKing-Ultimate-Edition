"""Check independent Be Prepared scenery/colors, native preservation and current save."""
import json,os,subprocess,re
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride944-save';out.mkdir(exist_ok=True);cases={};r=json.loads((ROOT/'build/later902-selected/report.json').read_text());base=r['command'].copy();i=base.index('--save-at');del base[i:i+3];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,extra,old,load in [('old-native','',True,'build/later902-selected/pride-rock.native.state'),('native','',False,'build/later902-selected/pride-rock.native.state'),('background','graphics.scenery.background = md\n',False,'build/later902-selected/pride-rock.native.state'),('colors','graphics.scenery.palettes = md\n',False,'build/later902-selected/pride-rock.native.state'),('both','graphics.scenery.background = md\ngraphics.scenery.palettes = md\n',False,'build/later902-selected/pride-rock.native.state'),('restored','graphics.scenery.background = md\ngraphics.scenery.palettes = md\n',False,'build/pride944-save/both/current.state')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/later910/player.exe' if old else 'build/pride943/player.exe'))
 for flag,value in (('--load',ROOT/load),('--input-polled',ROOT/'build/later902-selected/after57000.polled.tape'),('--frames',57240),('--hash-at',57240),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 cmd[cmd.index('--sprite-assets')+1]=str(ROOT/('build/later909-helper/sprites.assets' if old else 'build/pride928-helper/sprites.assets'))
 if name=='restored':
  # Neutral input on both branches keeps this renderer/save comparison local.
  pass
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+extra);(folder/'neutral.polled.tape').write_bytes(bytes(2000));cmd[cmd.index('--input-polled')+1]=str(folder/'neutral.polled.tape')
 if name=='both':cmd+=['--save-at','57120',str(folder/'current.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
 s=json.loads((folder/'scene.json').read_text());cases[name]=dict(command=cmd,window_sha256=digest(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),level=s['level'],gameplay=s['latched_gameplay']);print(name,s['level'],s['latched_gameplay']['health'],flush=True)
c=cases;checks=dict(native_preserved=c['old-native']['window_sha256']==c['native']['window_sha256'] and c['old-native']['guest']==c['native']['guest'],all_choices_guest_preserved=len({tuple(sorted(v['guest'].items())) for v in c.values()})==1,independent_picture_choices=len({c[k]['window_sha256'] for k in ('native','background','colors','both')})==4,current_save_picture=c['both']['window_sha256']==c['restored']['window_sha256'],all_healthy=all(v['level']==9 and v['gameplay']['health']>0 for v in c.values()))
paths=[Path(__file__),ROOT/'build/pride943/build-report.json',ROOT/'build/later902-selected/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
