"""Preserve the first qualified sampler build before removing per-pixel setting searches."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next750-performance-baseline';out.mkdir();name='engine/runner/tlk_wide.c';p=ROOT/name;q=out/name;q.parent.mkdir(parents=True);shutil.copyfile(p,q)
(out/'report.json').write_text(json.dumps(dict(historical_sources={name:dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())}),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next746-correction-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next750-performance-baseline')"))
