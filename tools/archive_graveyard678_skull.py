"""Preserve current opening-skull sources before targeted gameplay/art changes."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard678-skull-baseline';out.mkdir()
names=['engine/runner/tlk_graveyard_gameplay.c','engine/runner/tlk_wide.c','engine/runner/tlk_resources.c','engine/runner/tlk_resources.h','engine/runner/aot_pace.h','tools/pride_sprite_catalog.py','tools/graveyard_sprite_catalog.py','engine/generated/resources/pride_sprite_map.h','scripts/RunInstalledPreview.ps1','scripts/Setup.ps1','docs/HANDOFF.md','docs/graveyard-resources.md','docs/graveyard-skull-feedback.md','engine/docs/devlog.md','game-data/install.json','profiles/graveyard-md.ini']
rows={}
for name in names:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
print('ARCHIVED',len(rows))
