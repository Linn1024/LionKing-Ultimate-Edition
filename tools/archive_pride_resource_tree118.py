"""Preserve current103/previous release bindings before semantic tree repair."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
assert bound(ROOT/'build/pride-hyena-probe103/build-report.json')['result']=='BUILT'
out=ROOT/'build/pride-resource-tree118-baseline';out.mkdir();rows={}
for name in ['engine/runner/tlk_resources.c','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hyena-probe.md','docs/pride-hyena-entrance.md','engine/docs/devlog.md','tools/pride_arena_history.py']:
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-hyena-probe103-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-resource-tree118-baseline')"))
print('Archived',len(rows),flush=True)
