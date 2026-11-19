"""Preserve qualified795/786 sources before the gorilla/palette extension."""
import json,shutil,re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna800-baseline';out.mkdir(exist_ok=True)
names=['engine/runner/tlk_'+n for n in ('wide.c','md_sprites.c','md_sprites.h','md_sprite_format.inc','resources.c','next_scene_data.c','next_scene_data.h')]
names+=['engine/generated/resources/pride_sprite_map.h','tools/pride_sprite_catalog.py','docs/HANDOFF.md','docs/all-levels-progress.md','engine/docs/devlog.md']
rows={}
for n in names:
 p=ROOT/n;q=out/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[n]=dict(sha256=digest(q),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
s=(ROOT/'engine/runner/tlk_resources.c').read_text();a=s.index('static TlkResourceNode nodes[]');b=s.index('\n};',a)
print('nodes',len(re.findall(r'^\s*\{"',s[a:b],re.M)));print(s[b-400:b])
