"""Freeze existing bindings before adding independent hyena walking probe height."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
assert bound(ROOT/'build/pride-menu-enable86/bindings/report.json')['result']=='PASS'
out=ROOT/'build/pride-hyena-probe97-baseline';out.mkdir();rows={}
for name in ['engine/runner/tlk_resources.c','engine/recomp/pride_hooks.json','engine/cmake/TlkPrideFinalPlayer.cmake',
             'docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-enemy-motion.md','engine/docs/devlog.md','tools/pride_arena_history.py']:
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-hyena-walk96-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-hyena-probe97-baseline')"))
print('Archived',len(rows),flush=True)
