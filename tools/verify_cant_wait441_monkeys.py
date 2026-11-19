"""One second-level ordinary moving scene: palette isolation and native output preservation."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait373/report.json';ref=bound(reference)
build=ROOT/'build/cant-wait440/build-report.json';bound(build)
out=ROOT/'build/cant-wait441-monkeys';out.mkdir(exist_ok=True)
manifest=ROOT/'game-data/install.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'));base=ref['commands']['moving'].copy()
for flag,n in (('--save-at',3),('--wav',2),('--wav-seconds',2)):
    i=base.index(flag);del base[i:i+n]
keys=(('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets'))
for flag,key in keys:base[base.index(flag)+1]=str(manifest.parent/m[key]['file'])
for flag,key in (('--rom','snes'),('--md-rom','megadrive')):base[base.index(flag)+1]=str(manifest.parent/m['roms'][key]['file'])
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};commands={};images={};guest={}
for name,exe,md in [('old',ROOT/'dist/installed-preview418/LionKing.exe',False),('native',build.parent/'player.exe',False),('md',build.parent/'player.exe',True)]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(exe)
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\n'+('graphics.sprites.animals.monkeys.palette = md\n' if md else ''))
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;images[name]=Image.open(folder/'window.png').convert('RGB')
    guest[name]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text());print('rendered',name,flush=True)
scene=json.loads((out/'md/scene.json').read_text());delta=ImageChops.difference(images['native'],images['md']);bbox=delta.getbbox();mask=Image.new('L',images['md'].size);draw=ImageDraw.Draw(mask);scale=images['md'].height//224;column=(images['md'].width//scale-256)//2
poses={int(p['native_pose'],16) for p in json.loads((ROOT/'build/cant-wait437-monkeys/report.json').read_text())['pairs']}
monkeys=0
for p in scene['pieces']:
    if p['pose'] not in poses or p['palette'] not in (2,3):continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column)*scale,y*scale,(x+column+n)*scale-1,(y+n)*scale-1),fill=255);monkeys+=1
outside=delta.copy();outside.paste((0,0,0),(0,0),mask)
checks=dict(exact_native_output=ImageChops.difference(images['old'],images['native']).getbbox() is None,guest_unchanged=bool(guest['old']) and all(v==guest['old'] for v in guest.values()),monkeys_present=monkeys>0,selected_colors_visible=bool(bbox),changes_only_monkey_draws=outside.getbbox() is None,actual_second_level=scene['level']==1 and scene['latched_gameplay']['descriptor']==0x3b9)
paths=[Path(__file__),reference,build,manifest,ROOT/'build/cant-wait437-monkeys/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,changed_bounds=bbox,commands=commands,scope='One moving/jumping/roaring second-level scene; previous native palette picture and all sampled guest fields retained. MD palette changes confined to monkey draws. No audio/behavior/save algorithm change or unrelated matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,'delta',bbox,flush=True)
