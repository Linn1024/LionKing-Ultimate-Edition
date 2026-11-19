"""Keep current139 release identities before recording new bounded contact evidence."""
import json
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
assert bound(ROOT/'build/pride-hyena-entrance139/bindings/report.json')['result']=='PASS'
base=ROOT/'build/pride-contact175-baseline';base.mkdir();rows={}
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-enemy-activation.md','docs/pride-actor-bounds.md','engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=base/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(base/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-hyena-entrance160-publish-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-contact175-baseline')"))
print('Archived139 documentation identities',flush=True)
