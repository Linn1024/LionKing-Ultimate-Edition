"""One current vulture checkpoint checks installed art, independent controls and unchanged gameplay."""
import json,os,re,struct,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard523-vultures/report.json';r=bound(reference)
build=ROOT/'build/graveyard530/build-report.json';bound(build)
helper=ROOT/'build/graveyard529-helper/build-report.json';bound(helper)
out=ROOT/'build/graveyard531-vultures';out.mkdir(exist_ok=True);commands={};images={};guest={};scenes={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,exe,extra in [('old',ROOT/'build/graveyard503/player.exe',''),('native',build.parent/'player.exe',''),('frames',build.parent/'player.exe','graphics.sprites.enemies.vultures.frames = md\n'),('palette',build.parent/'player.exe','graphics.sprites.enemies.vultures.palette = md\n')]:
    folder=out/label;folder.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(exe)
    for flag,count in (('--save-at',3),('--input-polled',2)):
        i=cmd.index(flag);del cmd[i:i+count]
    cmd[cmd.index('--load')+1]=str(reference.parent/'enemies.state')
    if label!='old':cmd[cmd.index('--sprite-assets')+1]=str(helper.parent/'sprites.assets')
    for flag,value in (('--frames','15001'),('--hash-at','15001'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+extra)
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd;images[label]=Image.open(folder/'window.png').convert('RGB');guest[label]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text());scenes[label]=json.loads((folder/'scene.json').read_text())
w,h=images['native'].size;scale=h//224;column=(w//scale-256)//2;mask=Image.new('L',(w,h));draw=ImageDraw.Draw(mask);count=0
owners={int(x,16) for x in json.loads((ROOT/'tools/graveyard_vulture_pairs.json').read_text())['native_descriptors']}
for p in scenes['native']['pieces']:
    if p['actor_descriptor'] not in owners or p['palette']!=5:continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column-12)*scale,(y-12)*scale,(x+column+n+12)*scale-1,(y+n+12)*scale-1),fill=255);count+=1
checks=dict(actual_graveyard=all(s['level']==2 and s['latched_gameplay']['descriptor']==0x3eb and s['latched_gameplay']['health']>0 for s in scenes.values()),vultures_present=count>0,native_output_preserved=ImageChops.difference(images['old'],images['native']).getbbox() is None,gameplay_preserved=bool(guest['old']) and all(g==guest['old'] for g in guest.values()))
for label in ('frames','palette'):
    delta=ImageChops.difference(images['native'],images[label]);outside=delta.copy();outside.paste((0,0,0),(0,0),mask)
    checks[label+'_visible']=delta.getbbox() is not None;checks[label+'_only_owned_vultures']=outside.getbbox() is None
checks['independent_outputs']=ImageChops.difference(images['frames'],images['palette']).getbbox() is not None
def assets(path):
    raw=path.read_bytes();count=struct.unpack_from('<I',raw,20)[0];at=192+416+17792;entries={}
    for _ in range(count):
        pose,a,b=struct.unpack_from('<3I',raw,at);at+=12;entries[pose]=raw[at:at+a+b];at+=a+b
    return raw[192:192+416+17792],entries,raw[at:]
old=assets(Path(commands['old'][commands['old'].index('--sprite-assets')+1]));new=assets(helper.parent/'sprites.assets')
checks['existing_art_gameplay_retained']=all(new[1].get(p)==image for p,image in old[1].items()) and old[2]==new[2]
checks['only_native_bank5_prepared']=old[0][:160]==new[0][:160] and old[0][192:]==new[0][192:]
checks['46_reviewed_images_added']=len(new[1])==len(old[1])+46
paths=[Path(__file__),reference,build,helper,ROOT/'build/graveyard528-vulture-map/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='Current save; one ordinary field per variant, native scenery. Vulture frames/colors independent; actual ownership, old art/gameplay/native output retained and only original native bank5 added to prepared palette payload.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
