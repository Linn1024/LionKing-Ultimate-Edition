"""Use the nearby encounter to verify independent gorilla artwork and palette."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
from pride_arena_history import bound
out=ROOT/'build/hakuna803-gorilla';out.mkdir(exist_ok=True);bound(ROOT/'build/hakuna802/build-report.json');base=json.loads((ROOT/'build/hakuna790-route/report.json').read_text())['cases'][-1]['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={}
profile=(ROOT/'build/hakuna796-simba/5-native/resources.ini').read_text();(out/'resources.ini').write_text(profile);(out/'host.ini').write_text('opengl = 0\nscale = 1\n')
state=native_fixture(ROOT/'build/hakuna790-route/34500/current.state',out/'entry.native.state',34500);cmd=base.copy();cmd[0]=str(ROOT/'build/hakuna802/player.exe')
for flag,value in (('--load',state),('--frames',35060),('--hash-at',35060),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--sprite-assets',ROOT/'build/hakuna801-helper/sprites.assets'),('--dump-window',out/'entry.png'),('--dump-scene',out/'entry.json')):cmd[cmd.index(flag)+1]=str(value)
i=cmd.index('--save-at');cmd[i+1:i+3]=['35060',str(out/'encounter.state')]
with (out/'entry.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
entry_command=cmd.copy();native_fixture(out/'encounter.state',out/'encounter.native.state',35060)
for name,extra in [('old',''),('native',''),('frames','graphics.sprites.enemies.gorilla.frames = md\n'),('palette','graphics.sprites.enemies.gorilla.palette = md\n'),('both','graphics.sprites.enemies.gorilla.frames = md\ngraphics.sprites.enemies.gorilla.palette = md\n')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=entry_command.copy();cmd[0]=str(ROOT/('build/hakuna795/player.exe' if name=='old' else 'build/hakuna802/player.exe'))
 for flag,count in (('--input-polled',2),('--save-at',3)):
  i=cmd.index(flag);del cmd[i:i+count]
 for flag,value in (('--load',out/'encounter.native.state'),('--frames',35080),('--hash-at',35080),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 if name=='old':cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/next741-helper/sprites.assets')
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text(profile+'\n'+extra)
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 text=(folder/'run.log').read_text();scene=json.loads((folder/'scene.json').read_text());sprites=json.loads((folder/'sprites.json').read_text());cases[name]=dict(command=cmd,guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',text,re.M)),scene=scene['latched_gameplay'],seen= sprites['seen_mapped_frames']);print(name,'used',sprites['seen_mapped_frames'],flush=True)
imgs={k:Image.open(out/k/'window.png').convert('RGB') for k in cases};scene=json.loads((out/'native/scene.json').read_text());mask=Image.new('L',imgs['native'].size);draw=ImageDraw.Draw(mask);column=(imgs['native'].width-256)//2;owned=0
for p in scene['pieces']:
 if p['actor_descriptor']==0xc58a7f and p['palette']==6:
  x,y=p['screen'];sz=p['size'];draw.rectangle((x+column-16,y-16,x+column+sz+16,y+sz+16),fill=255);owned+=1
checks=dict(actual_gorilla=owned>0,native_picture_preserved=ImageChops.difference(imgs['old'],imgs['native']).getbbox() is None,guest_state_preserved=len({tuple(sorted(c['guest'].items())) for c in cases.values()})==1,prepared_gorilla_used=cases['frames']['seen']>0 and cases['both']['seen']>0)
for k in ('frames','palette','both'):
 delta=ImageChops.difference(imgs['native'],imgs[k]);checks[k+'_visible']=delta.getbbox() is not None;delta.paste((0,0,0),(0,0),mask);checks[k+'_only_gorilla']=delta.getbbox() is None
checks['independent_choices']=ImageChops.difference(imgs['frames'],imgs['both']).getbbox() is not None and ImageChops.difference(imgs['palette'],imgs['both']).getbbox() is not None
paths=[Path(__file__),ROOT/'build/hakuna802/build-report.json',ROOT/'build/hakuna801-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,entry_command=entry_command,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
