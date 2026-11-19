"""Direct level-two rhino area: prepared-art preservation and scoped graphics."""
import json,os,re,struct,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait441-monkeys/report.json';r=bound(reference)
build=ROOT/'build/cant-wait460/build-report.json';bound(build)
helper=ROOT/'build/cant-wait459-helper/build-report.json';bound(helper)
out=ROOT/'build/cant-wait461-rhino';out.mkdir(exist_ok=True)
base=r['commands']['native'].copy();base[base.index('--frames')+1]='1500';base[base.index('--hash-at')+1]='1500'
tape=out/'approach.tape';tape.write_bytes(struct.pack('<1500H',*([0]*1250+[0x100]*55+[0]*195)));base[base.index('--input')+1]=str(tape)
commands={};images={};guest={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,exe,selected in [('old',ROOT/'dist/installed-preview448/LionKing.exe',False),('native',build.parent/'player.exe',False),('md',build.parent/'player.exe',True)]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(exe)
    if name!='old':cmd[cmd.index('--sprite-assets')+1]=str(helper.parent/'sprites.assets')
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\n'+('graphics.sprites.animals.rhinos = md\n' if selected else ''))
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;images[name]=Image.open(folder/'window.png').convert('RGB');guest[name]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text());print('rendered',name,flush=True)
scene=json.loads((out/'md/scene.json').read_text());delta=ImageChops.difference(images['native'],images['md']);bbox=delta.getbbox()
mask=Image.new('L',images['md'].size);draw=ImageDraw.Draw(mask);scale=images['md'].height//224;column=(images['md'].width//scale-256)//2;rhinos=0
for p in scene['pieces']:
    if p.get('actor_descriptor')!=0xc58c14:continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column-40)*scale,(y-60)*scale,(x+column+n+40)*scale,(y+n+60)*scale),fill=255);rhinos+=1
outside=delta.copy();outside.paste((0,0,0),(0,0),mask)
def assets(path):
    p=path.read_bytes();count=struct.unpack_from('<I',p,20)[0];at=192+416+17792;entries={}
    for _ in range(count):
        pose,a,b=struct.unpack_from('<3I',p,at);at+=12;entries[pose]=p[at:at+a+b];at+=a+b
    return p[192:192+416+17792],entries,p[at:]
old=assets(Path(base[base.index('--sprite-assets')+1]));new=assets(helper.parent/'sprites.assets')
checks=dict(existing_prepared_art_retained=old[0]==new[0] and all(new[1].get(k)==v for k,v in old[1].items()),gameplay_records_retained=old[2]==new[2],only13_art_entries_added=len(new[1])==len(old[1])+13,exact_native_picture=ImageChops.difference(images['old'],images['native']).getbbox() is None,guest_unchanged=bool(guest['old']) and all(v==guest['old'] for v in guest.values()),rhino_draws_present=rhinos>0,selected_art_visible=bool(bbox),changes_scoped_to_rhino=outside.getbbox() is None,actual_second_level=scene['level']==1 and scene['latched_gameplay']['descriptor']==0x3b9)
paths=[Path(__file__),reference,build,helper]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,changed_bounds=bbox,commands=commands,scope='Direct level1 select (second stage), short rightward approach. Native controls, prepared shared artwork/gameplay retention and rhino-only rendered changes; no level1 replay or unrelated matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,'delta',bbox,flush=True)
