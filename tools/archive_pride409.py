"""Preserve the long historical handoff before consolidating current status."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride409-baseline';out.mkdir();records={}
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
history=ROOT/'docs/history';history.mkdir(exist_ok=True)
for name,target in (('docs/HANDOFF.md','handoff-through403.md'),('docs/pride-lands-status.md','pride-status-through403.md')):
    path=history/target;assert not path.exists();shutil.copy2(ROOT/name,path)
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride397-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride409-baseline')"))
print('Preserved full handoff/status history and bound source identities.')
