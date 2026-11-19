"""Preserve bound handoff identities before recording current runtime gates."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride-menu242-baseline';out.mkdir();records={}
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-source.md',
             'engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;copy=out/name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,copy)
    records[name]=dict(sha256=digest(p),archive=copy.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
print('ARCHIVED',len(records),flush=True)
