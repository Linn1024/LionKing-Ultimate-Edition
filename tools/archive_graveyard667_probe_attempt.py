"""Retain the unsuccessful query-height prototype, then restore the published gameplay/resource scope."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard667-probe-attempt-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_hyena_probe.c','engine/runner/tlk_resources.c','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records,scope='MD walking query applied in666 but the held skull jump/landing trace remained identical; not shipped as a fix.'),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard663-hyena-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard667-probe-attempt-baseline')"))
for name in ('engine/runner/tlk_hyena_probe.c','engine/runner/tlk_resources.c'):shutil.copy2(ROOT/'build/graveyard663-hyena-baseline'/name,ROOT/name)
