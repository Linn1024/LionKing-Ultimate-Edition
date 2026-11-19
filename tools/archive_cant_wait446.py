"""Preserve published440 sources before adding independent ostrich colors."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait446-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_cw_monkey_metadata.h','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait438-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('cant-wait446-baseline')"))
