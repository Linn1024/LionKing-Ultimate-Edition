"""Preserve published118 identities before entrance-window integration."""
import json
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
assert bound(ROOT/'build/pride-resource-tree118/bindings/report.json')['result']=='PASS'
base=ROOT/'build/pride-hyena-entrance138-baseline';base.mkdir();rows={}
for name in ('engine/recomp/pride_hooks.json','engine/cmake/TlkPrideFinalPlayer.cmake','engine/runner/tlk_resources.c','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-hyena-entrance.md','docs/pride-lands-status.md','engine/docs/devlog.md'):
    p=ROOT/name;q=base/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(base/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-resource-publish123-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-hyena-entrance138-baseline')"))
print('Archived published118 identities',flush=True)
