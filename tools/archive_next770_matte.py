"""Preserve the backdrop investigation build before the verified matte-slot mapping."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next770-matte-baseline';out.mkdir();name='engine/runner/tlk_wide.c';p=ROOT/name;q=out/name;q.parent.mkdir(parents=True);shutil.copyfile(p,q)
(out/'report.json').write_text(json.dumps(dict(historical_sources={name:dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())}),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next765-backdrop-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next770-matte-baseline')"))
