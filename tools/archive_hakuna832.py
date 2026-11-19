"""Preserve qualified actor/HUD sources before later-level sound work."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna832-baseline';out.mkdir(exist_ok=True);rows={}
for name in ['engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','engine/runner/tlk_native_audio_owner.c','engine/runner/tlk_roar.c','engine/runner/tlk_wide.c','docs/HANDOFF.md','docs/all-levels-progress.md','engine/docs/devlog.md']:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(q),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
