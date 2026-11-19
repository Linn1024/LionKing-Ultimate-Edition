"""Qualify retained537 windows/logs with the actual platform metadata schema, without replay."""
import json,re
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard522-enemies/report.json';r=bound(reference)
build=ROOT/'build/graveyard536/build-report.json';bound(build)
proof=ROOT/'build/graveyard534-bones/report.json';bound(proof)
retained=ROOT/'build/graveyard537-bones';images={n:Image.open(retained/n/'window.png').convert('RGB') for n in ('old','native','md')};guest={n:re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(retained/n/'run.log').read_text()) for n in images}
scene=json.loads((retained/'md/scene.json').read_text());delta=ImageChops.difference(images['native'],images['md']);w,h=delta.size;scale=h//224;column=(w//scale-256)//2;mask=Image.new('L',(w,h));draw=ImageDraw.Draw(mask);count=0
for p in scene['pieces']:
    if p['palette']!=7 or p['actor_descriptor'] not in (0xc58e1c,0xc58e36,0xc58e50,0xc58e6a):continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column)*scale,y*scale,(x+column+n)*scale-1,(y+n)*scale-1),fill=255);count+=1
outside=delta.copy();outside.paste((0,0,0),(0,0),mask)
checks=dict(exact_native_output=ImageChops.difference(images['old'],images['native']).getbbox() is None,gameplay_unchanged=bool(guest['old']) and all(g==guest['old'] for g in guest.values()),platforms_present=count>0,selected_colors_visible=delta.getbbox() is not None,changes_only_platforms=outside.getbbox() is None,actual_graveyard=scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['health']>0)
cmd=r['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3];i=cmd.index('--input-polled');del cmd[i:i+2]
cmd[0]=str(build.parent/'player.exe');cmd[cmd.index('--load')+1]=str(reference.parent/'enemies.state');cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard529-helper/sprites.assets')
for flag,value in (('--frames','14251'),('--hash-at','14251'),('--config',str(retained/'native/host.ini')),('--resource-profile',str(retained/'native/resources.ini')),('--dump-window',str(retained/'native/window.png')),('--dump-scene',str(retained/'native/scene.json'))):cmd[cmd.index(flag)+1]=value
out=ROOT/'build/graveyard540-bones-qualified';out.mkdir(exist_ok=True)
paths=[Path(__file__),ROOT/'tools/verify_graveyard537_bones.py',reference,build,proof,*[p for n in images for p in (retained/n).rglob('*') if p.is_file()]]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=dict(native=cmd),scope='All three537 game processes rendered successfully; verifier then failed on inherited monkey native_pose key before analysis. Reuses those actual images/logs with correct platform ownership and third-level scene guard; no runtime fix or rerun.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
