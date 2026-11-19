"""One direct-selected scene: shared MD HUD extension changes only the HUD."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait462-rhino/report.json';r=bound(reference)
build=ROOT/'build/cant-wait482/build-report.json';bound(build)
out=ROOT/'build/cant-wait483-hud';out.mkdir(exist_ok=True);commands={};images={};guest={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,exe in [('old',ROOT/'build/cant-wait473/player.exe'),('new',build.parent/'player.exe')]:
    folder=out/label;folder.mkdir(exist_ok=True);cmd=r['commands']['native'].copy();cmd[0]=str(exe)
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/name)
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.hud.frames = md\n')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd;images[label]=Image.open(folder/'window.png').convert('RGB');guest[label]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
delta=ImageChops.difference(images['old'],images['new']);w,h=delta.size
regions={'roar':(0,0,w//2,h//4),'health':(w//2,0,w,h//4),'lives':(0,h*3//4,w//3,h)}
outside=delta.copy()
for box in regions.values():outside.paste((0,0,0),box)
checks={name+'_md_art_visible':delta.crop(box).getbbox() is not None for name,box in regions.items()}
checks.update(gameplay_unchanged=bool(guest['old']) and guest['old']==guest['new'],only_hud_changed=outside.getbbox() is None)
paths=[Path(__file__),reference,build,ROOT/'build/cant-wait479-hud-source/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,changed_bounds=delta.getbbox(),scope='Direct level2 select, same short approach. Existing shared cub HUD renderer is now eligible in the owned second-level scene; all three components change, world and guest sample retained.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
