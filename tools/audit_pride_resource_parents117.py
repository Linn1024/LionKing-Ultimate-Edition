"""Audit compiled103 table parents against semantic resource IDs before new nodes."""
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

bp=ROOT/'build/pride-hyena-probe103/build-report.json';build=bound(bp)
cmd=build['compiles']['resources'];source=Path(cmd[cmd.index('-c')+1]);text=source.read_text()
start=text.index('static const TlkResourceNode nodes[]');end=text.index('};',start)
rows=re.findall(r'^\s*\{"([^"]+)",\s*"[^"]*",\s*(-?\d+),',text[start:end],re.M)
assert len(rows)==136
nodes=[dict(index=i,id=name,parent=int(parent)) for i,(name,parent) in enumerate(rows)]
bad=[]
for node in nodes[1:]:
    parent=nodes[node['parent']]
    if node['parent'] and not node['id'].startswith(parent['id']+'.'):
        bad.append(dict(**node,parent_id=parent['id']))
out=ROOT/'build/pride-resource-parents117';out.mkdir()
paths=[Path(__file__),bp,source]
(out/'report.json').write_text(json.dumps(dict(result='RESOURCE_PARENT_MISMATCHES_OBSERVED' if bad else 'PARENTS_CONSISTENT',nodes=nodes,mismatches=bad,
    scope='Numeric parent values in the exact source compiled into103 resources, not a runtime behavioral or rendering check.',production_changed=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Resource nodes',len(nodes),'mismatches',bad,flush=True)
