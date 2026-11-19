"""Focused HUD artwork isolation and unchanged existing whole-HUD output."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/pride411-save/report.json';ref=bound(reference)
build=ROOT/'build/pride418/build-report.json';bound(build)
out=ROOT/'build/pride419-hud';out.mkdir(exist_ok=True)
base=ref['commands']['seed'].copy()
for flag,n in (('--save-at',3),('--input-polled',2)):
    i=base.index(flag);del base[i:i+n]
base+=['--practice-level','0']
base[base.index('--frames')+1]='1500';base[base.index('--hash-at')+1]='1500'
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
commands={};guest={};images={}
for name,exe,lines in [('native',build.parent/'player.exe',[]),('whole',build.parent/'player.exe',['graphics.hud.frames = md']),*[(k,build.parent/'player.exe',['graphics.hud.frames.'+k+' = md']) for k in ('roar','health','lives')],('old-native',ROOT/'dist/installed-preview398/LionKing.exe',[]),('old-whole',ROOT/'dist/installed-preview398/LionKing.exe',['graphics.hud.frames = md'])]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(exe)
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/file)
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+'\n'.join(lines)+'\n')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;guest[name]=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
    images[name]=Image.open(folder/'window.png').convert('RGB');print('rendered',name,flush=True)
checks={};diffs={};native=images['native'];whole=images['whole'];w,h=native.size
# Meter areas at Y16 and portrait/counter at Y200, scaled by the actual client.
boxes={'roar':(0,0,w//2,h//4),'health':(w//2,0,w,h//4),'lives':(0,h*3//4,w//2,h)}
for kind in boxes:
    delta=ImageChops.difference(native,images[kind]);bbox=delta.getbbox();diffs[kind]=bbox
    box=boxes[kind];checks[kind+'_visible']=bool(bbox)
    remainder=delta.copy();remainder.paste((0,0,0),box);checks[kind+'_isolated']=remainder.getbbox() is None
    checks[kind+'_matches_md_component']=ImageChops.difference(images[kind].crop(box),whole.crop(box)).getbbox() is None
checks['existing_native_unchanged']=ImageChops.difference(native,images['old-native']).getbbox() is None
checks['existing_whole_md_unchanged']=ImageChops.difference(whole,images['old-whole']).getbbox() is None
checks['guest_unchanged']=bool(guest['native']) and all(rows==guest['native'] for rows in guest.values())
checks['audio_unchanged']=len({digest(out/name/'audio.wav') for name in images})==1
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,differences=diffs,commands=commands,guest=guest,scope='One fixed Pride practice scene. Each child-only MD selection changes only its own HUD region and matches the same component of whole MD. Old whole/native pictures and guest/audio retained. SDL window dumps; separate live interaction/capture required.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
