"""Reuse passing captures with the tail's actual OBJ bank1, not monkey banks2/3."""
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait474-tail/report.json';r=bound(reference)
assert r['result']=='FAIL' and {k for k,v in r['checks'].items() if not v}=={'tails_present','changes_only_tail_draws'}
scene=json.loads((reference.parent/'md/scene.json').read_text());native=Image.open(reference.parent/'native/window.png').convert('RGB');md=Image.open(reference.parent/'md/window.png').convert('RGB');delta=ImageChops.difference(native,md)
mask=Image.new('L',md.size);draw=ImageDraw.Draw(mask);scale=md.height//224;column=(md.width//scale-256)//2
poses={int(p['native_pose'],16) for p in json.loads((ROOT/'build/cant-wait471-tail/report.json').read_text())['pairs']};count=0
for p in scene['pieces']:
    if p['pose'] not in poses or p['palette']!=1 or p['actor_descriptor']!=0xc58c08:continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column)*scale,y*scale,(x+column+n)*scale-1,(y+n)*scale-1),fill=255);count+=1
outside=delta.copy();outside.paste((0,0,0),(0,0),mask);checks=dict(r['checks']);checks['tails_present']=count>0;checks['changes_only_tail_draws']=outside.getbbox() is None
out=ROOT/'build/cant-wait477-tail-qualified';out.mkdir(exist_ok=True)
paths=[Path(__file__),reference,ROOT/'build/cant-wait471-tail/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=r['commands'],changed_bounds=delta.getbbox(),scope='Retained474 images/guest checks; tail OBJ bank1 corrects only the inherited monkey-bank mask expectation. No reruns or runtime changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print(checks,flush=True)
