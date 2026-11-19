"""Preserve802 sources before completing later-scene actors and action art."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna811-baseline';out.mkdir(exist_ok=True)
names=['engine/runner/tlk_'+x for x in ('wide.c','md_sprites.c','md_sprites.h','resources.c','next_scene_data.c','next_scene_data.h','roar.c','md_sprite_format.inc')]
names+=['engine/generated/resources/pride_sprite_map.h','tools/hakuna_gorilla_pairs.json','tools/hakuna_sprite_catalog.py','tools/pride_sprite_catalog.py','docs/HANDOFF.md','docs/all-levels-progress.md','engine/docs/devlog.md']
rows={}
for n in names:
 p=ROOT/n;q=out/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[n]=dict(sha256=digest(q),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n');print('Archived',len(rows))
