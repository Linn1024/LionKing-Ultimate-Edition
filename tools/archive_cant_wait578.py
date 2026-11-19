"""Freeze qualified combined sound candidate before second-level Continue audio ownership fix."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait578-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_audio.c','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait571-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('cant-wait578-baseline')"))
