"""Preserve sources before separating the three HUD artwork choices."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride417-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_resources.h','engine/runner/tlk_wide.c','docs/HANDOFF.md','docs/pride-lands-status.md','engine/docs/devlog.md','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride415-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride417-baseline')"))
