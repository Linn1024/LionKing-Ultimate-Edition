"""Focused opening-skull convergence, native control and socket art/color choices."""
import json,os,subprocess,csv,re
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/graveyard684/build-report.json';b=bound(build);helper=ROOT/'build/graveyard683-helper/build-report.json';bound(helper)
out=ROOT/'build/graveyard685-skull';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/graveyard675-matched-middle/report.json').read_text())['command'];commands={};traces={};windows={};logs={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
cases=[('md',1950,True,''),('native-control',1950,True,'game = snes\ndisplay.viewport = md\n'),('old-native',1950,False,'game = snes\ndisplay.viewport = md\n')]
for choice in ('all','frames','palette','native'):
 cases.append(('eyes-'+choice,1690,True,'graphics.sprites.enemies.hyenas.frames = '+('md' if choice in ('all','frames') else 'snes')+'\ngraphics.sprites.enemies.hyenas.palette = '+('md' if choice in ('all','palette') else 'snes')+'\n'))
for label,field,new,extra in cases:
 folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(build.parent/'player.exe') if new else base[0]
 for flag,value in (('--frames',str(field)),('--hash-at',str(field)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 if new:cmd[cmd.index('--sprite-assets')+1]=str(helper.parent/'sprites.assets')
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\n'+extra)
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv'),TLK_GRAVEYARD_GAMEPLAY_TRACE=str(folder/'gameplay.csv'),TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 commands[label]=cmd;traces[label]=list(csv.DictReader((folder/'actors.csv').open()));windows[label]=Image.open(folder/'window.png').convert('RGB');logs[label]=(folder/'run.log').read_text();print(label,'done',flush=True)
changes=[];previous={}
for row in traces['md']:
 if previous.get(row['actor'])!=row['action']:changes.append(row);previous[row['actor']]=row['action']
print([(x['field'],x['actor'],x['x'],x['action']) for x in changes],flush=True)
checks=dict(native_guest_preserved=re.findall(r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+',logs['native-control'])==re.findall(r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+',logs['old-native']),native_window_preserved=ImageChops.difference(windows['native-control'],windows['old-native']).getbbox() is None,md_walks_outward=any(r['actor']=='b693' and int(r['x'])>=1248 and r['action']=='c13c83' for r in traces['md']),socket_frames_visible=ImageChops.difference(windows['eyes-frames'],windows['eyes-native']).getbbox() is not None,socket_colors_visible=ImageChops.difference(windows['eyes-palette'],windows['eyes-native']).getbbox() is not None,socket_choices_independent=ImageChops.difference(windows['eyes-frames'],windows['eyes-palette']).getbbox() is not None)
paths=[Path(__file__),build,helper,ROOT/'build/graveyard675-matched-middle/report.json',ROOT/'build/graveyard657-md-skull/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,md_changes=changes,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
