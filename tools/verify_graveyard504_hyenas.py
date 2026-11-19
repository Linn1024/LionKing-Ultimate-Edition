"""One checkpoint field verifies independent Graveyard hyena art/colors and native preservation."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard490-entry/report.json';r=bound(reference)
build=ROOT/'build/graveyard503/build-report.json';bound(build)
out=ROOT/'build/graveyard504-hyenas';out.mkdir(exist_ok=True);commands={};images={};guest={};scenes={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,exe,extra in [('old',ROOT/'build/graveyard493/player.exe',''),('native',build.parent/'player.exe',''),('frames',build.parent/'player.exe','graphics.sprites.enemies.hyenas.frames = md\n'),('palette',build.parent/'player.exe','graphics.sprites.enemies.hyenas.palette = md\n')]:
    folder=out/label;folder.mkdir(exist_ok=True);cmd=r['commands']['native'].copy();cmd[0]=str(exe)
    for flag,count in (('--save-at',3),('--practice-level',2)):
        i=cmd.index(flag);del cmd[i:i+count]
    cmd+=['--load',str(reference.parent/'native/entry.state')]
    for flag,value in (('--frames','1801'),('--hash-at','1801'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.hud.frames = md\n'+extra)
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd;images[label]=Image.open(folder/'window.png').convert('RGB');guest[label]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text());scenes[label]=json.loads((folder/'scene.json').read_text())
w,h=images['native'].size;scale=h//224;column=(w//scale-256)//2;mask=Image.new('L',(w,h));draw=ImageDraw.Draw(mask);count=0
for p in scenes['native']['pieces']:
    if p['actor_descriptor']!=0xc58c74 or p['palette']!=6:continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column-8)*scale,(y-8)*scale,(x+column+n+8)*scale-1,(y+n+8)*scale-1),fill=255);count+=1
checks=dict(actual_graveyard=all(s['level']==2 and s['latched_gameplay']['descriptor']==0x3eb and s['latched_gameplay']['health']>0 for s in scenes.values()),hyenas_present=count>0,native_output_preserved=ImageChops.difference(images['old'],images['native']).getbbox() is None,gameplay_preserved=bool(guest['old']) and all(g==guest['old'] for g in guest.values()))
for label in ('frames','palette'):
    delta=ImageChops.difference(images['native'],images[label]);outside=delta.copy();outside.paste((0,0,0),(0,0),mask)
    checks[label+'_visible']=delta.getbbox() is not None;checks[label+'_only_owned_hyenas']=outside.getbbox() is None
checks['independent_outputs']=ImageChops.difference(images['frames'],images['palette']).getbbox() is not None
paths=[Path(__file__),reference,build,ROOT/'build/graveyard501-hyena-source/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='Reuses current entry checkpoint; one field per variant. Scenery remains SNES, so MD hyena palette is independent of scenery choice. Native game values/frames unchanged; preserved existing pose mappings and palette/ownership guards.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
