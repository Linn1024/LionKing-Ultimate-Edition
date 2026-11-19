"""One short direct-selected Graveyard view checks the three shared HUD components."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard490-entry/report.json';r=bound(reference)
build=ROOT/'build/graveyard493/build-report.json';bound(build)
out=ROOT/'build/graveyard494-hud';out.mkdir(exist_ok=True);commands={};images={};guest={};checks={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,exe in [('old',ROOT/'build/cant-wait482/player.exe'),('new',build.parent/'player.exe')]:
    folder=out/label;folder.mkdir(exist_ok=True);cmd=r['commands']['md'].copy();cmd[0]=str(exe)
    i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/name)
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
    (folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud.frames = md\n')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd;images[label]=Image.open(folder/'window.png').convert('RGB');guest[label]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
    scene=json.loads((folder/'scene.json').read_text());checks[label+'_actual_graveyard']=scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['health']>0
delta=ImageChops.difference(images['old'],images['new']);w,h=delta.size
regions={'roar':(0,0,w//2,h//4),'health':(w//2,0,w,h//4),'lives':(0,h*3//4,w//3,h)};outside=delta.copy()
for name,box in regions.items():checks[name+'_md_art_visible']=delta.crop(box).getbbox() is not None;outside.paste((0,0,0),box)
checks.update(gameplay_unchanged=bool(guest['old']) and guest['old']==guest['new'],only_hud_changed=outside.getbbox() is None)
paths=[Path(__file__),reference,build,ROOT/'build/graveyard491-hud-source/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,changed_bounds=delta.getbbox(),scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
