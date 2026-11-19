"""Preserve qualified actor builds before enabling the prepared adult HUD portrait."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna828-baseline';out.mkdir(exist_ok=True);rows={}
for name in ['engine/runner/tlk_md_hud.c','engine/runner/tlk_md_hud.h','engine/runner/tlk_wide.c','engine/runner/tlk_resources.c','docs/HANDOFF.md','docs/all-levels-progress.md','engine/docs/devlog.md']:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(q),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
