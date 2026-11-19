"""Preserve815 actor qualification before extending the reviewed image repertoire."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna820-baseline';out.mkdir(exist_ok=True);rows={}
names=['engine/generated/resources/pride_sprite_map.h','tools/hakuna_destiny_actor_pairs.json','tools/hakuna_gorilla_pairs.json','tools/hakuna_sprite_catalog.py','tools/pride_sprite_catalog.py','docs/HANDOFF.md','docs/all-levels-progress.md','engine/docs/devlog.md']
for name in names:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(q),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
