"""Preserve prior public launcher and active task documents before Graveyard sound publication."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard614-delivery-baseline';out.mkdir();records={}
for name in ('scripts/RunInstalledPreview.ps1','docs/HANDOFF.md','docs/graveyard-sound-gameplay-goal.md','docs/graveyard-goal.md','docs/graveyard-delivery-review.md','docs/graveyard-resources.md','docs/next-levels-status.md','docs/launchers.md','engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard608-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard614-delivery-baseline')"))
