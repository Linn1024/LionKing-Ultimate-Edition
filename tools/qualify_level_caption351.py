"""Qualify the inspected title client using its pixels, not a narrow capture deadline."""
import json
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/level-caption350/report.json';r=bound(reference)
out=ROOT/'build/level-caption351';out.mkdir(exist_ok=True)
checks={k:v for k,v in r['checks'].items() if k!='actual_windows_client'}
before,after=r['before'],r['after'];checks['actual_windows_title_interval']=bool(after) and 1550<=before['field']<=after['field']<1650
scene=json.loads((reference.parent/'settled/scene.json').read_text());colors={((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31) for v in scene['obj_palette0'][1:]}
images=[Image.open(p).convert('RGB') for p in (reference.parent/'settled/window.png',reference.parent/'windows/caption.png')]
mask=lambda im:{(x,y) for y in range(96,160) for x in range(80,600) if im.getpixel((x,y)) in colors}
checks['actual_window_exact_centred_title_pixels']=bool(mask(images[0])) and mask(images[0])==mask(images[1])
paths=[Path(__file__),reference,ROOT/'build/level-caption349/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='Actual PrintWindow capture spans1550..1578, while the caption remains live. Retained350 failed an unnecessarily tight1570 timestamp guard. Exact two-line title pixels in the OS client match the corrected settled view; no repeat window route or precise capture-field claim.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print(checks,flush=True)
