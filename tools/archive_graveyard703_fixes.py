"""Preserve sources and installed policy before fixing the four Graveyard audit findings."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard703-fix-baseline';out.mkdir()
names=['engine/runner/'+x for x in ('tlk_wide.c','tlk_audio.c','tlk_hyena_audio.c','tlk_roar.c','tlk_hitboxes.c','tlk_graveyard_gameplay.c','tlk_resources.c','tlk_resources.h','tlk_death_scene.c')]
names+=['docs/HANDOFF.md','docs/graveyard-coverage-audit.md','docs/graveyard-hyena-sound-audit.md','docs/graveyard-resources.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','game-data/install.json','profiles/graveyard-md.ini']
rows={}
for name in names:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n');print('ARCHIVED',len(rows))
