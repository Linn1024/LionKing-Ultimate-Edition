"""Preserve published86 documentation identities before recording new AI evidence."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

assert bound(ROOT/'build/pride-menu-enable86/bindings/report.json')['result']=='PASS'
out=ROOT/'build/pride-hyena-walk96-baseline';out.mkdir()
rows={}
for name in ['docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-enemy-motion.md','tools/pride_arena_history.py']:
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';source=p.read_text()
anchor="    folders.append('pride-menu-publish86-baseline')";assert source.count(anchor)==1
p.write_text(source.replace(anchor,anchor+"\n    folders.append('pride-hyena-walk96-baseline')"))
print('Archived published86 evidence sources',len(rows),flush=True)
